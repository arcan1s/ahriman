#
# Copyright (c) 2021 ahriman team.
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

import copy
import logging

from dataclasses import asdict, dataclass
from pathlib import Path
from pyalpm import vercmp  # type: ignore
from srcinfo.parse import parse_srcinfo  # type: ignore
from typing import Any, Dict, Iterable, List, Optional, Set, Type

from ahriman.core.alpm.aur import AUR
from ahriman.core.alpm.pacman import Pacman
from ahriman.core.exceptions import InvalidPackageInfo
from ahriman.core.util import check_output
from ahriman.models.package_description import PackageDescription
from ahriman.models.package_source import PackageSource
from ahriman.models.repository_paths import RepositoryPaths


@dataclass
class Package:
    """
    package properties representation
    :ivar aur_url: AUR root url
    :ivar base: package base name
    :ivar packages: map of package names to their properties. Filled only on load from archive
    :ivar version: package full version
    """

    base: str
    version: str
    aur_url: str
    packages: Dict[str, PackageDescription]

    _check_output = check_output

    @property
    def depends(self) -> List[str]:
        """
        :return: sum of dependencies per arch package
        """
        return sorted(set(sum([package.depends for package in self.packages.values()], start=[])))

    @property
    def git_url(self) -> str:
        """
        :return: package git url to clone
        """
        return f"{self.aur_url}/{self.base}.git"

    @property
    def groups(self) -> List[str]:
        """
        :return: sum of groups per each package
        """
        return sorted(set(sum([package.groups for package in self.packages.values()], start=[])))

    @property
    def is_single_package(self) -> bool:
        """
        :return: true in case if this base has only one package with the same name
        """
        return self.base in self.packages and len(self.packages) == 1

    @property
    def is_vcs(self) -> bool:
        """
        :return: True in case if package base looks like VCS package and false otherwise
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
        :return: sum of licenses per each package
        """
        return sorted(set(sum([package.licenses for package in self.packages.values()], start=[])))

    @property
    def web_url(self) -> str:
        """
        :return: package AUR url
        """
        return f"{self.aur_url}/packages/{self.base}"

    @classmethod
    def from_archive(cls: Type[Package], path: Path, pacman: Pacman, aur_url: str) -> Package:
        """
        construct package properties from package archive
        :param path: path to package archive
        :param pacman: alpm wrapper instance
        :param aur_url: AUR root url
        :return: package properties
        """
        package = pacman.handle.load_pkg(str(path))
        return cls(package.base, package.version, aur_url,
                   {package.name: PackageDescription.from_package(package, path)})

    @classmethod
    def from_aur(cls: Type[Package], name: str, aur_url: str) -> Package:
        """
        construct package properties from AUR page
        :param name: package name (either base or normal name)
        :param aur_url: AUR root url
        :return: package properties
        """
        package = AUR.info(name)
        return cls(package.package_base, package.version, aur_url, {package.name: PackageDescription()})

    @classmethod
    def from_build(cls: Type[Package], path: Path, aur_url: str) -> Package:
        """
        construct package properties from sources directory
        :param path: path to package sources directory
        :param aur_url: AUR root url
        :return: package properties
        """
        srcinfo, errors = parse_srcinfo((path / ".SRCINFO").read_text())
        if errors:
            raise InvalidPackageInfo(errors)
        packages = {key: PackageDescription() for key in srcinfo["packages"]}
        version = cls.full_version(srcinfo.get("epoch"), srcinfo["pkgver"], srcinfo["pkgrel"])

        return cls(srcinfo["pkgbase"], version, aur_url, packages)

    @classmethod
    def from_json(cls: Type[Package], dump: Dict[str, Any]) -> Package:
        """
        construct package properties from json dump
        :param dump: json dump body
        :return: package properties
        """
        packages = {
            key: PackageDescription.from_json(value)
            for key, value in dump.get("packages", {}).items()
        }
        return Package(
            base=dump["base"],
            version=dump["version"],
            aur_url=dump["aur_url"],
            packages=packages)

    @classmethod
    def load(cls: Type[Package], package: str, source: PackageSource, pacman: Pacman, aur_url: str) -> Package:
        """
        package constructor from available sources
        :param package: one of path to sources directory, path to archive or package name/base
        :param source: source of the package required to define the load method
        :param pacman: alpm wrapper instance (required to load from archive)
        :param aur_url: AUR root url
        :return: package properties
        """
        try:
            resolved_source = source.resolve(package)
            if resolved_source == PackageSource.Archive:
                return cls.from_archive(Path(package), pacman, aur_url)
            if resolved_source == PackageSource.AUR:
                return cls.from_aur(package, aur_url)
            if resolved_source == PackageSource.Local:
                return cls.from_build(Path(package), aur_url)
            raise InvalidPackageInfo(f"Unsupported local package source {resolved_source}")
        except InvalidPackageInfo:
            raise
        except Exception as e:
            raise InvalidPackageInfo(str(e))

    @staticmethod
    def dependencies(path: Path) -> Set[str]:
        """
        load dependencies from package sources
        :param path: path to package sources directory
        :return: list of package dependencies including makedepends array, but excluding packages from this base
        """
        # additional function to remove versions from dependencies
        def trim_version(name: str) -> str:
            for symbol in ("<", "=", ">"):
                name = name.split(symbol)[0]
            return name

        srcinfo, errors = parse_srcinfo((path / ".SRCINFO").read_text())
        if errors:
            raise InvalidPackageInfo(errors)
        makedepends = srcinfo.get("makedepends", [])
        # sum over each package
        depends: List[str] = srcinfo.get("depends", [])
        for package in srcinfo["packages"].values():
            depends.extend(package.get("depends", []))
        # we are not interested in dependencies inside pkgbase
        packages = set(srcinfo["packages"].keys())
        full_list = set(depends + makedepends) - packages
        return {trim_version(package_name) for package_name in full_list}

    @staticmethod
    def full_version(epoch: Optional[str], pkgver: str, pkgrel: str) -> str:
        """
        generate full version from components
        :param epoch: package epoch if any
        :param pkgver: package version
        :param pkgrel: package release version (arch linux specific)
        :return: generated version
        """
        prefix = f"{epoch}:" if epoch else ""
        return f"{prefix}{pkgver}-{pkgrel}"

    def actual_version(self, paths: RepositoryPaths) -> str:
        """
        additional method to handle VCS package versions
        :param paths: repository paths instance
        :return: package version if package is not VCS and current version according to VCS otherwise
        """
        if not self.is_vcs:
            return self.version

        from ahriman.core.build_tools.sources import Sources

        logger = logging.getLogger("build_details")
        Sources.load(paths.cache_for(self.base), self.git_url, None)

        try:
            # update pkgver first
            Package._check_output("makepkg", "--nodeps", "--nobuild",
                                  exception=None, cwd=paths.cache_for(self.base), logger=logger)
            # generate new .SRCINFO and put it to parser
            srcinfo_source = Package._check_output("makepkg", "--printsrcinfo",
                                                   exception=None, cwd=paths.cache_for(self.base), logger=logger)
            srcinfo, errors = parse_srcinfo(srcinfo_source)
            if errors:
                raise InvalidPackageInfo(errors)

            return self.full_version(srcinfo.get("epoch"), srcinfo["pkgver"], srcinfo["pkgrel"])
        except Exception:
            logger.exception("cannot determine version of VCS package, make sure that you have VCS tools installed")

        return self.version

    def full_depends(self, pacman: Pacman, packages: Iterable[Package]) -> List[str]:
        """
        generate full dependencies list including transitive dependencies
        :param pacman: alpm wrapper instance
        :param packages: repository package list
        :return: all dependencies of the package
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

    def is_outdated(self, remote: Package, paths: RepositoryPaths, calculate_version: bool = True) -> bool:
        """
        check if package is out-of-dated
        :param remote: package properties from remote source
        :param paths: repository paths instance. Required for VCS packages cache
        :param calculate_version: expand version to actual value (by calculating git versions)
        :return: True if the package is out-of-dated and False otherwise
        """
        remote_version = remote.actual_version(paths) if calculate_version else remote.version
        result: int = vercmp(self.version, remote_version)
        return result < 0

    def pretty_print(self) -> str:
        """
        generate pretty string representation
        :return: print-friendly string
        """
        details = "" if self.is_single_package else f""" ({" ".join(sorted(self.packages.keys()))})"""
        return f"{self.base}{details}"

    def view(self) -> Dict[str, Any]:
        """
        generate json package view
        :return: json-friendly dictionary
        """
        return asdict(self)
