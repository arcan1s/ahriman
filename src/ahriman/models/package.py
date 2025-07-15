#
# Copyright (c) 2021-2026 ahriman team.
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
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from pyalpm import vercmp  # type: ignore[import-not-found]
from typing import Any, Self

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.alpm.remote import AUR, Official, OfficialSyncdb
from ahriman.core.log import LazyLogging
from ahriman.core.utils import dataclass_view, full_version, list_flatmap, parse_version, srcinfo_property_list
from ahriman.models.package_description import PackageDescription
from ahriman.models.package_source import PackageSource
from ahriman.models.pkgbuild import Pkgbuild
from ahriman.models.remote_source import RemoteSource


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
        :attr:`ahriman.models.package_source.PackageSource.Repository` respectively:

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
        return list_flatmap(self.packages.values(), lambda package: package.depends)

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
        return list_flatmap(self.packages.values(), lambda package: package.check_depends)

    @property
    def depends_make(self) -> list[str]:
        """
        get package make dependencies

        Returns:
            list[str]: sum of make dependencies per each package
        """
        return list_flatmap(self.packages.values(), lambda package: package.make_depends)

    @property
    def depends_opt(self) -> list[str]:
        """
        get package optional dependencies

        Returns:
            list[str]: sum of optional dependencies per each package
        """
        return list_flatmap(self.packages.values(), lambda package: package.opt_depends)

    @property
    def groups(self) -> list[str]:
        """
        get package base groups

        Returns:
            list[str]: sum of groups per each package
        """
        return list_flatmap(self.packages.values(), lambda package: package.groups)

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
        return list_flatmap(self.packages.values(), lambda package: package.licenses)

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
            base=package.base or package.name,
            version=package.version,
            remote=RemoteSource(source=PackageSource.Archive),
            packages={package.name: description},
            packager=package.packager,
        )

    @classmethod
    def from_aur(cls, name: str, packager: str | None = None, *, include_provides: bool = False) -> Self:
        """
        construct package properties from AUR page

        Args:
            name(str): package name (either base or normal name)
            packager(str | None, optional): packager to be used for this build (Default value = None)
            include_provides(bool, optional): search by provides if no exact match found (Default value = False)

        Returns:
            Self: package properties
        """
        package = AUR.info(name, include_provides=include_provides)

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
        """
        pkgbuild = Pkgbuild.from_file(path / "PKGBUILD")

        packages = {
            package: PackageDescription(
                depends=srcinfo_property_list("depends", pkgbuild, properties, architecture=architecture),
                make_depends=srcinfo_property_list("makedepends", pkgbuild, properties, architecture=architecture),
                opt_depends=srcinfo_property_list("optdepends", pkgbuild, properties, architecture=architecture),
                check_depends=srcinfo_property_list("checkdepends", pkgbuild, properties, architecture=architecture),
            )
            for package, properties in pkgbuild.packages().items()
        }
        version = full_version(pkgbuild.get("epoch"), pkgbuild["pkgver"], pkgbuild["pkgrel"])

        remote = RemoteSource(
            source=PackageSource.Local,
            git_url=path.absolute().as_uri(),
            web_url=None,
            path=".",
            branch="master",
        )

        return cls(
            base=pkgbuild["pkgbase"],
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
    def from_official(cls, name: str, pacman: Pacman, packager: str | None = None, *, use_syncdb: bool = True,
                      include_provides: bool = False) -> Self:
        """
        construct package properties from official repository page

        Args:
            name(str): package name (either base or normal name)
            pacman(Pacman): alpm wrapper instance
            packager(str | None, optional): packager to be used for this build (Default value = None)
            use_syncdb(bool, optional): use pacman databases instead of official repositories RPC (Default value = True)
            include_provides(bool, optional): search by provides if no exact match found (Default value = False)

        Returns:
            Self: package properties
        """
        impl = OfficialSyncdb if use_syncdb else Official
        package = impl.info(name, pacman=pacman, include_provides=include_provides)

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

        if self.vercmp(local_version) > 0:
            return None  # upstream version is newer than local one, keep upstream pkgrel

        *_, local_pkgrel = parse_version(local_version)
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

    def vercmp(self, version: str) -> int:
        """
        typed wrapper around :func:`pyalpm.vercmp()`

        Args:
            version(str): version to compare

        Returns:
            int: negative if current version is less than provided, positive if greater than and zero if equals
        """
        result: int = vercmp(self.version, version)
        return result

    def view(self) -> dict[str, Any]:
        """
        generate json package view

        Returns:
            dict[str, Any]: json-friendly dictionary
        """
        return dataclass_view(self)

    def with_packages(self, packages: Iterable[Path], pacman: Pacman) -> None:
        """
        replace packages descriptions with ones from archives

        Args:
            packages(Iterable[Path]): paths to package archives
            pacman(Pacman): alpm wrapper instance
        """
        self.packages = {}  # reset state
        for package in packages:
            archive = self.from_archive(package, pacman)
            if archive.base != self.base:
                continue

            self.packages.update(archive.packages)
