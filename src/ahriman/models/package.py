#
# Copyright (c) 2021-2024 ahriman team.
#
# This file is part of ahriman
# (see https://github.com/arcan1s/ahriman).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# pylint: disable=too-many-lines,too-many-public-methods
from __future__ import annotations

import copy

from collections.abc import Callable, Generator, Iterable
from dataclasses import dataclass
from pathlib import Path
from pyalpm import vercmp  # type: ignore[import-not-found]
from srcinfo.parse import parse_srcinfo  # type: ignore[import-untyped]
from typing import Any, Self
from urllib.parse import urlparse

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.alpm.remote import AUR, Official, OfficialSyncdb
from ahriman.core.exceptions import PackageInfoError
from ahriman.core.log import LazyLogging
from ahriman.core.utils import check_output, dataclass_view, full_version, parse_version, srcinfo_property_list, utcnow
from ahriman.models.package_description import PackageDescription
from ahriman.models.package_source import PackageSource
from ahriman.models.remote_source import RemoteSource
from ahriman.models.repository_paths import RepositoryPaths


@dataclass(kw_only=True)
class Package(LazyLogging):
    """
    package properties representation

    Attributes:
        base(str): package base name
        packager(str | None): package packager if available
        packages(dict[str, PackageDescription): map of package names to their properties.
            Filled only on load from archive
        remote(RemoteSource): package remote source if applicable
        version(str): package full version

    Examples:
        Different usages of this class may generate different (incomplete) data, e.g. if instantiating class from json::

            >>> package = Package.from_json(dump)

        it will contain every data available in the json body. Otherwise, if generate package from local archive::

            >>> package = Package.from_archive(local_path, pacman)

        it will probably miss file descriptions (in case if there are multiple packages which belong to the base).

        The specific class load method must be defined based on the source provided. The following methods (mostly) must
        be used: :func:`from_archive()`, :func:`from_aur()`, :func:`from_build()`, :func:`from_official()` for sources
        :attr:`ahriman.models.package_source.PackageSource.Archive`,
        :attr:`ahriman.models.package_source.PackageSource.AUR`,
        :attr:`ahriman.models.package_source.PackageSource.Local` and
        :attr:`ahriman.models.package_source.PackageSource.Repository` repsectively:

            >>> ahriman_package = Package.from_aur("ahriman")
            >>> pacman_package = Package.from_official("pacman", pacman)
    """

    base: str
    version: str
    remote: RemoteSource
    packages: dict[str, PackageDescription]
    packager: str | None = None

    @property
    def depends(self) -> list[str]:
        """
        get package base dependencies

        Returns:
            list[str]: sum of dependencies per each package
        """
        return self._package_list_property(lambda package: package.depends)

    @property
    def depends_build(self) -> set[str]:
        """
        get full list of external dependencies which has to be installed for build process

        Returns:
            set[str]: full dependencies list used by devtools
        """
        return (set(self.depends) | set(self.depends_make) | set(self.depends_check)).difference(self.packages_full)

    @property
    def depends_check(self) -> list[str]:
        """
        get package test dependencies

        Returns:
            list[str]: sum of test dependencies per each package
        """
        return self._package_list_property(lambda package: package.check_depends)

    @property
    def depends_make(self) -> list[str]:
        """
        get package make dependencies

        Returns:
            list[str]: sum of make dependencies per each package
        """
        return self._package_list_property(lambda package: package.make_depends)

    @property
    def depends_opt(self) -> list[str]:
        """
        get package optional dependencies

        Returns:
            list[str]: sum of optional dependencies per each package
        """
        return self._package_list_property(lambda package: package.opt_depends)

    @property
    def groups(self) -> list[str]:
        """
        get package base groups

        Returns:
            list[str]: sum of groups per each package
        """
        return self._package_list_property(lambda package: package.groups)

    @property
    def is_single_package(self) -> bool:
        """
        is it possible to transform package base to single package or not

        Returns:
            bool: true in case if this base has only one package with the same name
        """
        return self.base in self.packages and len(self.packages) == 1

    @property
    def is_vcs(self) -> bool:
        """
        get VCS flag based on the package base

        Returns:
            bool: ``True`` in case if package base looks like VCS package and ``False`` otherwise
        """
        return self.base.endswith("-bzr") \
            or self.base.endswith("-csv") \
            or self.base.endswith("-darcs") \
            or self.base.endswith("-git") \
            or self.base.endswith("-hg") \
            or self.base.endswith("-svn")

    @property
    def licenses(self) -> list[str]:
        """
        get package base licenses

        Returns:
            list[str]: sum of licenses per each package
        """
        return self._package_list_property(lambda package: package.licenses)

    @property
    def packages_full(self) -> list[str]:
        """
        get full packages list including provides

        Returns:
            list[str]: full list of packages which this base contains
        """
        packages = set()
        for package, properties in self.packages.items():
            packages.add(package)
            packages.update(properties.provides)
        return sorted(packages)

    @classmethod
    def from_archive(cls, path: Path, pacman: Pacman) -> Self:
        """
        construct package properties from package archive

        Args:
            path(Path): path to package archive
            pacman(Pacman): alpm wrapper instance

        Returns:
            Self: package properties
        """
        package = pacman.handle.load_pkg(str(path))
        description = PackageDescription.from_package(package, path)
        return cls(
            base=package.base,
            version=package.version,
            remote=RemoteSource(source=PackageSource.Archive),
            packages={package.name: description},
            packager=package.packager,
        )

    @classmethod
    def from_aur(cls, name: str, packager: str | None = None) -> Self:
        """
        construct package properties from AUR page

        Args:
            name(str): package name (either base or normal name)
            packager(str | None, optional): packager to be used for this build (Default value = None)

        Returns:
            Self: package properties
        """
        package = AUR.info(name)

        remote = RemoteSource(
            source=PackageSource.AUR,
            git_url=AUR.remote_git_url(package.package_base, package.repository),
            web_url=AUR.remote_web_url(package.package_base),
            path=".",
            branch="master",
        )

        return cls(
            base=package.package_base,
            version=package.version,
            remote=remote,
            packages={package.name: PackageDescription.from_aur(package)},
            packager=packager,
        )

    @classmethod
    def from_build(cls, path: Path, architecture: str, packager: str | None = None) -> Self:
        """
        construct package properties from sources directory

        Args:
            path(Path): path to package sources directory
            architecture(str): load package for specific architecture
            packager(str | None, optional): packager to be used for this build (Default value = None)

        Returns:
            Self: package properties

        Raises:
            PackageInfoError: if there are parsing errors
        """
        srcinfo_source = check_output("makepkg", "--printsrcinfo", cwd=path)
        srcinfo, errors = parse_srcinfo(srcinfo_source)
        if errors:
            raise PackageInfoError(errors)

        packages = {
            package: PackageDescription(
                depends=srcinfo_property_list("depends", srcinfo, properties, architecture=architecture),
                make_depends=srcinfo_property_list("makedepends", srcinfo, properties, architecture=architecture),
                opt_depends=srcinfo_property_list("optdepends", srcinfo, properties, architecture=architecture),
                check_depends=srcinfo_property_list("checkdepends", srcinfo, properties, architecture=architecture),
            )
            for package, properties in srcinfo["packages"].items()
        }
        version = full_version(srcinfo.get("epoch"), srcinfo["pkgver"], srcinfo["pkgrel"])

        remote = RemoteSource(
            source=PackageSource.Local,
            git_url=path.absolute().as_uri(),
            web_url=None,
            path=".",
            branch="master",
        )

        return cls(
            base=srcinfo["pkgbase"],
            version=version,
            remote=remote,
            packages=packages,
            packager=packager,
        )

    @classmethod
    def from_json(cls, dump: dict[str, Any]) -> Self:
        """
        construct package properties from json dump

        Args:
            dump(dict[str, Any]): json dump body

        Returns:
            Self: package properties
        """
        packages_json = dump.get("packages") or {}
        packages = {
            key: PackageDescription.from_json(value)
            for key, value in packages_json.items()
        }
        remote = dump.get("remote") or {}
        return cls(
            base=dump["base"],
            version=dump["version"],
            remote=RemoteSource.from_json(remote),
            packages=packages,
            packager=dump.get("packager"),
        )

    @classmethod
    def from_official(cls, name: str, pacman: Pacman, packager: str | None = None, *, use_syncdb: bool = True) -> Self:
        """
        construct package properties from official repository page

        Args:
            name(str): package name (either base or normal name)
            pacman(Pacman): alpm wrapper instance
            packager(str | None, optional): packager to be used for this build (Default value = None)
            use_syncdb(bool, optional): use pacman databases instead of official repositories RPC (Default value = True)

        Returns:
            Self: package properties
        """
        package = OfficialSyncdb.info(name, pacman=pacman) if use_syncdb else Official.info(name)

        remote = RemoteSource(
            source=PackageSource.Repository,
            git_url=Official.remote_git_url(package.package_base, package.repository),
            web_url=Official.remote_web_url(package.package_base),
            path=".",
            branch="main",
        )

        return cls(
            base=package.package_base,
            version=package.version,
            remote=remote,
            packages={package.name: PackageDescription.from_aur(package)},
            packager=packager,
        )

    @staticmethod
    def local_files(path: Path) -> Generator[Path, None, None]:
        """
        extract list of local files

        Args:
            path(Path): path to package sources directory

        Yields:
            Path: list of paths of files which belong to the package and distributed together with this tarball.
            All paths are relative to the ``path``

        Raises:
            PackageInfoError: if there are parsing errors
        """
        srcinfo_source = check_output("makepkg", "--printsrcinfo", cwd=path)
        srcinfo, errors = parse_srcinfo(srcinfo_source)
        if errors:
            raise PackageInfoError(errors)

        # we could use arch property, but for consistency it is better to call special method
        architectures = Package.supported_architectures(path)

        for architecture in architectures:
            for source in srcinfo_property_list("source", srcinfo, {}, architecture=architecture):
                if "::" in source:
                    _, source = source.split("::", 1)  # in case if filename is specified, remove it

                if urlparse(source).scheme:
                    # basically file schema should use absolute path which is impossible if we are distributing
                    # files together with PKGBUILD. In this case we are going to skip it also
                    continue

                yield Path(source)

        if (install := srcinfo.get("install", None)) is not None:
            yield Path(install)

    @staticmethod
    def supported_architectures(path: Path) -> set[str]:
        """
        load supported architectures from package sources

        Args:
            path(Path): path to package sources directory

        Returns:
            set[str]: list of package supported architectures

        Raises:
            PackageInfoError: if there are parsing errors
        """
        srcinfo_source = check_output("makepkg", "--printsrcinfo", cwd=path)
        srcinfo, errors = parse_srcinfo(srcinfo_source)
        if errors:
            raise PackageInfoError(errors)
        return set(srcinfo.get("arch", []))

    def _package_list_property(self, extractor: Callable[[PackageDescription], list[str]]) -> list[str]:
        """
        extract list property from single packages and combine them into one list

        Notes:
            Basically this method is generic for type of ``list[T]``, but there is no trait ``Comparable`` in default
        packages, thus we limit this method only to new types

        Args:
            extractor(Callable[[PackageDescription], list[str]): package property extractor

        Returns:
            list[str]: combined list of unique entries in properties list
        """
        def generator() -> Generator[str, None, None]:
            for package in self.packages.values():
                yield from extractor(package)

        return sorted(set(generator()))

    def actual_version(self, paths: RepositoryPaths) -> str:
        """
        additional method to handle VCS package versions

        Args:
            paths(RepositoryPaths): repository paths instance

        Returns:
            str: package version if package is not VCS and current version according to VCS otherwise

        Raises:
            PackageInfoError: if there are parsing errors
        """
        if not self.is_vcs:
            return self.version

        from ahriman.core.build_tools.sources import Sources

        Sources.load(paths.cache_for(self.base), self, [], paths)

        try:
            # update pkgver first
            check_output("makepkg", "--nodeps", "--nobuild", cwd=paths.cache_for(self.base), logger=self.logger)
            # generate new .SRCINFO and put it to parser
            srcinfo_source = check_output("makepkg", "--printsrcinfo",
                                          cwd=paths.cache_for(self.base), logger=self.logger)
            srcinfo, errors = parse_srcinfo(srcinfo_source)
            if errors:
                raise PackageInfoError(errors)

            return full_version(srcinfo.get("epoch"), srcinfo["pkgver"], srcinfo["pkgrel"])
        except Exception:
            self.logger.exception("cannot determine version of VCS package, make sure that VCS tools are installed")

        return self.version

    def full_depends(self, pacman: Pacman, packages: Iterable[Package]) -> list[str]:
        """
        generate full dependencies list including transitive dependencies

        Args:
            pacman(Pacman): alpm wrapper instance
            packages(Iterable[Package]): repository package list

        Returns:
            list[str]: all dependencies of the package
        """
        dependencies = {}
        # load own package dependencies
        for package_base in packages:
            for name, repo_package in package_base.packages.items():
                dependencies[name] = repo_package.depends
                for provides in repo_package.provides:
                    dependencies[provides] = repo_package.depends
        # load repository dependencies
        for database in pacman.handle.get_syncdbs():
            for pacman_package in database.pkgcache:
                dependencies[pacman_package.name] = pacman_package.depends
                for provides in pacman_package.provides:
                    dependencies[provides] = pacman_package.depends

        result = set(self.depends)
        current_depends: set[str] = set()
        while result != current_depends:
            current_depends = copy.deepcopy(result)
            for package in current_depends:
                result.update(dependencies.get(package, []))

        return sorted(result)

    def is_newer_than(self, timestamp: float | int) -> bool:
        """
        check if package was built after the specified timestamp

        Args:
            timestamp(float | int): timestamp to check build date against

        Returns:
            bool: ``True`` in case if package was built after the specified date and ``False`` otherwise.
            In case if build date is not set by any of packages, it returns False
        """
        return any(
            package.build_date > timestamp
            for package in self.packages.values()
            if package.build_date is not None
        )

    def is_outdated(self, remote: Package, paths: RepositoryPaths, *,
                    vcs_allowed_age: float | int = 0,
                    calculate_version: bool = True) -> bool:
        """
        check if package is out-of-dated

        Args:
            remote(Package): package properties from remote source
            paths(RepositoryPaths): repository paths instance. Required for VCS packages cache
            vcs_allowed_age(float | int, optional): max age of the built packages before they will be
                forced to calculate actual version (Default value = 0)
            calculate_version(bool, optional): expand version to actual value (by calculating git versions)
                (Default value = True)

        Returns:
            bool: ``True`` if the package is out-of-dated and ``False`` otherwise
        """
        min_vcs_build_date = utcnow().timestamp() - vcs_allowed_age
        if calculate_version and not self.is_newer_than(min_vcs_build_date):
            remote_version = remote.actual_version(paths)
        else:
            remote_version = remote.version

        result: int = vercmp(self.version, remote_version)
        return result < 0

    def next_pkgrel(self, local_version: str | None) -> str | None:
        """
        generate next pkgrel variable. The package release will be incremented if ``local_version`` is more or equal to
        the :attr:`version`; in this case the function will return new pkgrel value, otherwise ``None`` will be
        returned

        Args:
            local_version(str | None): locally stored package version if available

        Returns:
            str | None: new generated package release version if any. In case if the release contains dot (e.g. 1.2),
            the minor part will be incremented by 1. If the release does not contain major.minor notation, the minor
            version equals to 1 will be appended
        """
        if local_version is None:
            return None  # local version not found, keep upstream pkgrel

        epoch, pkgver, _ = parse_version(self.version)
        local_epoch, local_pkgver, local_pkgrel = parse_version(local_version)

        if epoch != local_epoch or pkgver != local_pkgver:
            return None  # epoch or pkgver are different, keep upstream pkgrel
        if vercmp(self.version, local_version) > 0:
            return None  # upstream version is newer than local one, keep upstream pkgrel

        if "." in local_pkgrel:
            major, minor = local_pkgrel.rsplit(".", maxsplit=1)
        else:
            major, minor = local_pkgrel, "0"

        return f"{major}.{int(minor) + 1}"

    def pretty_print(self) -> str:
        """
        generate pretty string representation

        Returns:
            str: print-friendly string
        """
        details = "" if self.is_single_package else f""" ({" ".join(sorted(self.packages.keys()))})"""
        return f"{self.base}{details}"

    def view(self) -> dict[str, Any]:
        """
        generate json package view

        Returns:
            dict[str, Any]: json-friendly dictionary
        """
        return dataclass_view(self)
