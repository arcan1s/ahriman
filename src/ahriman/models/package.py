#
# Copyright (c) 2021-2023 ahriman team.
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
# pylint: disable=too-many-lines
from __future__ import annotations

import copy

from dataclasses import asdict, dataclass
from pathlib import Path
from pyalpm import vercmp  # type: ignore
from srcinfo.parse import parse_srcinfo  # type: ignore
from typing import Any, Dict, Iterable, List, Optional, Set, Type, Union

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.alpm.remote import AUR, Official, OfficialSyncdb
from ahriman.core.exceptions import PackageInfoError
from ahriman.core.log import LazyLogging
from ahriman.core.util import check_output, full_version
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
        packages(Dict[str, PackageDescription): map of package names to their properties.
            Filled only on load from archive
        remote(Optional[RemoteSource]): package remote source if applicable
        version(str): package full version

    Examples:
        Different usages of this class may generate different (incomplete) data, e.g. if instantiating class from json::

            >>> package = Package.from_json(dump)

        it will contain every data available in the json body. Otherwise, if generate package from local archive::

            >>> package = Package.from_archive(local_path, pacman, remote=None)

        it will probably miss file descriptions (in case if there are multiple packages which belong to the base).

        The specific class load method must be defined based on the source provided. The following methods (mostly) must
        be used: ``from_archive``, ``from_aur``, ``from_build``, ``from_official`` for sources
        ``PackageSource.Archive``, ``PackageSource.AUR``, ``PackageSource.Local`` and ``PackageSource.Repository``
        repsectively:

            >>> ahriman_package = Package.from_aur("ahriman", pacman)
            >>> pacman_package = Package.from_official("pacman", pacman)
    """

    base: str
    version: str
    remote: Optional[RemoteSource]
    packages: Dict[str, PackageDescription]

    _check_output = check_output

    @property
    def depends(self) -> List[str]:
        """
        get package base dependencies

        Returns:
            List[str]: sum of dependencies per each package
        """
        return sorted(set(sum((package.depends for package in self.packages.values()), start=[])))

    @property
    def groups(self) -> List[str]:
        """
        get package base groups

        Returns:
            List[str]: sum of groups per each package
        """
        return sorted(set(sum((package.groups for package in self.packages.values()), start=[])))

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
            bool: True in case if package base looks like VCS package and False otherwise
        """
        return self.base.endswith("-bzr") \
            or self.base.endswith("-csv")\
            or self.base.endswith("-darcs")\
            or self.base.endswith("-git")\
            or self.base.endswith("-hg")\
            or self.base.endswith("-svn")

    @property
    def licenses(self) -> List[str]:
        """
        get package base licenses

        Returns:
            List[str]: sum of licenses per each package
        """
        return sorted(set(sum((package.licenses for package in self.packages.values()), start=[])))

    @classmethod
    def from_archive(cls: Type[Package], path: Path, pacman: Pacman, remote: Optional[RemoteSource]) -> Package:
        """
        construct package properties from package archive

        Args:
            path(Path): path to package archive
            pacman(Pacman): alpm wrapper instance
            remote(RemoteSource): package remote source if applicable

        Returns:
            Package: package properties
        """
        package = pacman.handle.load_pkg(str(path))
        description = PackageDescription.from_package(package, path)
        return cls(base=package.base, version=package.version, remote=remote, packages={package.name: description})

    @classmethod
    def from_aur(cls: Type[Package], name: str, pacman: Pacman) -> Package:
        """
        construct package properties from AUR page

        Args:
            name(str): package name (either base or normal name)
            pacman(Pacman): alpm wrapper instance

        Returns:
            Package: package properties
        """
        package = AUR.info(name, pacman=pacman)
        remote = RemoteSource.from_source(PackageSource.AUR, package.package_base, package.repository)
        return cls(
            base=package.package_base,
            version=package.version,
            remote=remote,
            packages={package.name: PackageDescription()})

    @classmethod
    def from_build(cls: Type[Package], path: Path) -> Package:
        """
        construct package properties from sources directory

        Args:
            path(Path): path to package sources directory

        Returns:
            Package: package properties

        Raises:
            InvalidPackageInfo: if there are parsing errors
        """
        srcinfo_source = Package._check_output("makepkg", "--printsrcinfo", cwd=path)
        srcinfo, errors = parse_srcinfo(srcinfo_source)
        if errors:
            raise PackageInfoError(errors)
        packages = {key: PackageDescription() for key in srcinfo["packages"]}
        version = full_version(srcinfo.get("epoch"), srcinfo["pkgver"], srcinfo["pkgrel"])

        return cls(base=srcinfo["pkgbase"], version=version, remote=None, packages=packages)

    @classmethod
    def from_json(cls: Type[Package], dump: Dict[str, Any]) -> Package:
        """
        construct package properties from json dump

        Args:
            dump(Dict[str, Any]): json dump body

        Returns:
            Package: package properties
        """
        packages = {
            key: PackageDescription.from_json(value)
            for key, value in dump.get("packages", {}).items()
        }
        remote = dump.get("remote", {})
        return cls(base=dump["base"], version=dump["version"], remote=RemoteSource.from_json(remote), packages=packages)

    @classmethod
    def from_official(cls: Type[Package], name: str, pacman: Pacman, *, use_syncdb: bool = True) -> Package:
        """
        construct package properties from official repository page

        Args:
            name(str): package name (either base or normal name)
            pacman(Pacman): alpm wrapper instance
            use_syncdb(bool, optional): use pacman databases instead of official repositories RPC (Default value = True)

        Returns:
            Package: package properties
        """
        package = OfficialSyncdb.info(name, pacman=pacman) if use_syncdb else Official.info(name, pacman=pacman)
        remote = RemoteSource.from_source(PackageSource.Repository, package.package_base, package.repository)
        return cls(
            base=package.package_base,
            version=package.version,
            remote=remote,
            packages={package.name: PackageDescription()})

    @staticmethod
    def dependencies(path: Path) -> Set[str]:
        """
        load dependencies from package sources

        Args:
            path(Path): path to package sources directory

        Returns:
            Set[str]: list of package dependencies including makedepends array, but excluding packages from this base

        Raises:
            InvalidPackageInfo: if there are parsing errors
        """
        # additional function to remove versions from dependencies
        def extract_packages(raw_packages_list: List[str]) -> Set[str]:
            return {trim_version(package_name) for package_name in raw_packages_list}

        def trim_version(package_name: str) -> str:
            for symbol in ("<", "=", ">"):
                package_name = package_name.split(symbol)[0]
            return package_name

        srcinfo_source = Package._check_output("makepkg", "--printsrcinfo", cwd=path)
        srcinfo, errors = parse_srcinfo(srcinfo_source)
        if errors:
            raise PackageInfoError(errors)
        makedepends = extract_packages(srcinfo.get("makedepends", []))
        # sum over each package
        depends = extract_packages(srcinfo.get("depends", []))
        for package in srcinfo["packages"].values():
            depends |= extract_packages(package.get("depends", []))
        # we are not interested in dependencies inside pkgbase
        packages = set(srcinfo["packages"].keys())
        return (depends | makedepends) - packages

    @staticmethod
    def supported_architectures(path: Path) -> Set[str]:
        """
        load supported architectures from package sources

        Args:
            path(Path): path to package sources directory

        Returns:
            Set[str]: list of package supported architectures

        Raises:
            InvalidPackageInfo: if there are parsing errors
        """
        srcinfo_source = Package._check_output("makepkg", "--printsrcinfo", cwd=path)
        srcinfo, errors = parse_srcinfo(srcinfo_source)
        if errors:
            raise PackageInfoError(errors)
        return set(srcinfo.get("arch", []))

    def actual_version(self, paths: RepositoryPaths) -> str:
        """
        additional method to handle VCS package versions

        Args:
            paths(RepositoryPaths): repository paths instance

        Returns:
            str: package version if package is not VCS and current version according to VCS otherwise

        Raises:
            InvalidPackageInfo: if there are parsing errors
        """
        if not self.is_vcs:
            return self.version

        from ahriman.core.build_tools.sources import Sources

        Sources.load(paths.cache_for(self.base), self, [], paths)

        try:
            # update pkgver first
            Package._check_output("makepkg", "--nodeps", "--nobuild",
                                  cwd=paths.cache_for(self.base), logger=self.logger)
            # generate new .SRCINFO and put it to parser
            srcinfo_source = Package._check_output("makepkg", "--printsrcinfo",
                                                   cwd=paths.cache_for(self.base), logger=self.logger)
            srcinfo, errors = parse_srcinfo(srcinfo_source)
            if errors:
                raise PackageInfoError(errors)

            return full_version(srcinfo.get("epoch"), srcinfo["pkgver"], srcinfo["pkgrel"])
        except Exception:
            self.logger.exception("cannot determine version of VCS package, make sure that VCS tools are installed")

        return self.version

    def full_depends(self, pacman: Pacman, packages: Iterable[Package]) -> List[str]:
        """
        generate full dependencies list including transitive dependencies

        Args:
            pacman(Pacman): alpm wrapper instance
            packages(Iterable[Package]): repository package list

        Returns:
            List[str]: all dependencies of the package
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
        current_depends: Set[str] = set()
        while result != current_depends:
            current_depends = copy.deepcopy(result)
            for package in current_depends:
                result.update(dependencies.get(package, []))

        return sorted(result)

    def is_newer_than(self, timestamp: Union[float, int]) -> bool:
        """
        check if package was built after the specified timestamp

        Args:
            timestamp(int): timestamp to check build date against

        Returns:
            bool: True in case if package was built after the specified date and False otherwise. In case if build date
                is not set by any of packages, it returns False
        """
        return any(
            package.build_date > timestamp
            for package in self.packages.values()
            if package.build_date is not None
        )

    def is_outdated(self, remote: Package, paths: RepositoryPaths, *, calculate_version: bool) -> bool:
        """
        check if package is out-of-dated

        Args:
            remote(Package): package properties from remote source
            paths(RepositoryPaths): repository paths instance. Required for VCS packages cache
            calculate_version(bool, optional): expand version to actual value (by calculating git versions)
                (Default value = True)

        Returns:
            bool: True if the package is out-of-dated and False otherwise
        """
        remote_version = remote.actual_version(paths) if calculate_version else remote.version
        result: int = vercmp(self.version, remote_version)
        return result < 0

    def pretty_print(self) -> str:
        """
        generate pretty string representation

        Returns:
            str: print-friendly string
        """
        details = "" if self.is_single_package else f""" ({" ".join(sorted(self.packages.keys()))})"""
        return f"{self.base}{details}"

    def view(self) -> Dict[str, Any]:
        """
        generate json package view

        Returns:
            Dict[str, Any]: json-friendly dictionary
        """
        return asdict(self)
