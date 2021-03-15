#
# Copyright (c) 2021 Evgenii Alekseev.
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

import aur  # type: ignore
import os
import shutil
import tempfile

from dataclasses import dataclass
from pyalpm import vercmp  # type: ignore
from srcinfo.parse import parse_srcinfo  # type: ignore
from typing import Dict, List, Optional, Set, Type

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.exceptions import InvalidPackageInfo
from ahriman.core.util import check_output
from ahriman.models.package_desciption import PackageDescription


@dataclass
class Package:
    '''
    package properties representation
    :ivar aurl_url: AUR root url
    :ivar base: package base name
    :ivar packages: map of package names to their properties. Filled only on load from archive
    :ivar version: package full version
    '''

    base: str
    version: str
    aur_url: str
    packages: Dict[str, PackageDescription]

    @property
    def git_url(self) -> str:
        '''
        :return: package git url to clone
        '''
        return f'{self.aur_url}/{self.base}.git'

    @property
    def is_vcs(self) -> bool:
        '''
        :return: True in case if package base looks like VCS package and false otherwise
        '''
        return self.base.endswith('-bzr') \
            or self.base.endswith('-csv')\
            or self.base.endswith('-darcs')\
            or self.base.endswith('-git')\
            or self.base.endswith('-hg')\
            or self.base.endswith('-svn')

    @property
    def web_url(self) -> str:
        '''
        :return: package AUR url
        '''
        return f'{self.aur_url}/packages/{self.base}'

    def actual_version(self) -> str:
        '''
        additional method to handle VCS package versions
        :return: package version if package is not VCS and current version according to VCS otherwise
        '''
        if not self.is_vcs:
            return self.version

        from ahriman.core.build_tools.task import Task
        clone_dir = tempfile.mkdtemp()
        try:
            Task.fetch(clone_dir, self.git_url)
            # update pkgver first
            check_output('makepkg', '--nodeps', '--nobuild',
                         exception=None, cwd=clone_dir)
            # generate new .SRCINFO and put it to parser
            src_info_source = check_output('makepkg', '--printsrcinfo',
                                           exception=None, cwd=clone_dir)
            src_info, errors = parse_srcinfo(src_info_source)
            if errors:
                raise InvalidPackageInfo(errors)
            return self.full_version(src_info.get('epoch'), src_info['pkgver'], src_info['pkgrel'])
        finally:
            shutil.rmtree(clone_dir, ignore_errors=True)

    @classmethod
    def from_archive(cls: Type[Package], path: str, pacman: Pacman, aur_url: str) -> Package:
        '''
        construct package properties from package archive
        :param path: path to package archive
        :param pacman: alpm wrapper instance
        :param aur_url: AUR root url
        :return: package properties
        '''
        package = pacman.handle.load_pkg(path)
        properties = PackageDescription(os.path.basename(path), package.isize)
        return cls(package.base, package.version, aur_url, {package.name: properties})

    @classmethod
    def from_aur(cls: Type[Package], name: str, aur_url: str) -> Package:
        '''
        construct package properties from AUR page
        :param name: package name (either base or normal name)
        :param aur_url: AUR root url
        :return: package properties
        '''
        package = aur.info(name)
        return cls(package.package_base, package.version, aur_url, {package.name: PackageDescription()})

    @classmethod
    def from_build(cls: Type[Package], path: str, aur_url: str) -> Package:
        '''
        construct package properties from sources directory
        :param path: path to package sources directory
        :param aur_url: AUR root url
        :return: package properties
        '''
        with open(os.path.join(path, '.SRCINFO')) as fn:
            src_info, errors = parse_srcinfo(fn.read())
        if errors:
            raise InvalidPackageInfo(errors)
        packages = {key: PackageDescription() for key in src_info['packages'].keys()}
        version = cls.full_version(src_info.get('epoch'), src_info['pkgver'], src_info['pkgrel'])

        return cls(src_info['pkgbase'], version, aur_url, packages)

    @staticmethod
    def dependencies(path: str) -> Set[str]:
        '''
        load dependencies from package sources
        :param path: path to package sources directory
        :return: list of package dependencies including makedepends array, but excluding packages from this base
        '''
        with open(os.path.join(path, '.SRCINFO')) as fn:
            src_info, errors = parse_srcinfo(fn.read())
        if errors:
            raise InvalidPackageInfo(errors)
        makedepends = src_info.get('makedepends', [])
        # sum over each package
        depends: List[str] = src_info.get('depends', [])
        for package in src_info['packages'].values():
            depends.extend(package.get('depends', []))
        # we are not interested in dependencies inside pkgbase
        packages = set(src_info['packages'].keys())
        return set(depends + makedepends) - packages

    @staticmethod
    def full_version(epoch: Optional[str], pkgver: str, pkgrel: str) -> str:
        '''
        generate full version from components
        :param epoch: package epoch if any
        :param pkgver: package version
        :param pkgrel: package release version (archlinux specific)
        :return: generated version
        '''
        prefix = f'{epoch}:' if epoch else ''
        return f'{prefix}{pkgver}-{pkgrel}'

    @staticmethod
    def load(path: str, pacman: Pacman, aur_url: str) -> Package:
        '''
        package constructor from available sources
        :param path: one of path to sources directory, path to archive or package name/base
        :param pacman: alpm wrapper instance (required to load from archive)
        :param aur_url: AUR root url
        :return: package properties
        '''
        try:
            if os.path.isdir(path):
                package: Package = Package.from_build(path, aur_url)
            elif os.path.exists(path):
                package = Package.from_archive(path, pacman, aur_url)
            else:
                package = Package.from_aur(path, aur_url)
            return package
        except InvalidPackageInfo:
            raise
        except Exception as e:
            raise InvalidPackageInfo(str(e))

    def is_outdated(self, remote: Package) -> bool:
        '''
        check if package is out-of-dated
        :param remote: package properties from remote source
        :return: True if the package is out-of-dated and False otherwise
        '''
        remote_version = remote.actual_version()  # either normal version or updated VCS
        result: int = vercmp(self.version, remote_version)
        return result < 0
