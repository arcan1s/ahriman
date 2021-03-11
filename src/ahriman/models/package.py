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

import aur
import os
import shutil
import tempfile

from dataclasses import dataclass, field
from srcinfo.parse import parse_srcinfo
from typing import Set, Type

from ahriman.core.exceptions import InvalidPackageInfo
from ahriman.core.util import check_output


@dataclass
class Package:
    base: str
    version: str
    aur_url: str
    packages: Set[str] = field(default_factory=set)

    @property
    def git_url(self) -> str:
        return f'{self.aur_url}/{self.base}.git'

    @property
    def is_vcs(self) -> bool:
        return self.base.endswith('-bzr') \
               or self.base.endswith('-csv')\
               or self.base.endswith('-darcs')\
               or self.base.endswith('-git')\
               or self.base.endswith('-hg')\
               or self.base.endswith('-svn')

    @property
    def web_url(self) -> str:
        return f'{self.aur_url}/packages/{self.base}'

    # additional method to handle vcs versions
    def actual_version(self) -> str:
        if not self.is_vcs:
            return self.version

        from ahriman.core.build_tools.task import Task
        clone_dir = tempfile.mkdtemp()
        try:
            Task.fetch(clone_dir, self.git_url)
            # update pkgver first
            check_output('makepkg', '--nodeps', '--noprepare', '--nobuild',
                         exception=None, cwd=clone_dir)
            # generate new .SRCINFO and put it to parser
            src_info_source = check_output('makepkg', '--printsrcinfo',
                                           exception=None, cwd=clone_dir)
            src_info, errors = parse_srcinfo(src_info_source)
            if errors:
                raise InvalidPackageInfo(errors)
            return f'{src_info["pkgver"]}-{src_info["pkgrel"]}'
        finally:
            shutil.rmtree(clone_dir, ignore_errors=True)

    @classmethod
    def from_archive(cls: Type[Package], path: str, aur_url: str) -> Package:
        package, base, version = check_output('expac', '-p', '%n %e %v', path, exception=None).split()
        return cls(base, version, aur_url, {package})

    @classmethod
    def from_aur(cls: Type[Package], name: str, aur_url: str)-> Package:
        package = aur.info(name)
        return cls(package.package_base, package.version, aur_url, {package.name})

    @classmethod
    def from_build(cls: Type[Package], path: str, aur_url: str) -> Package:
        with open(os.path.join(path, '.SRCINFO')) as fn:
            src_info, errors = parse_srcinfo(fn.read())
        if errors:
            raise InvalidPackageInfo(errors)
        packages = set(src_info['packages'].keys())

        return cls(src_info['pkgbase'], f'{src_info["pkgver"]}-{src_info["pkgrel"]}', aur_url, packages)

    @staticmethod
    def load(path: str, aur_url: str) -> Package:
        try:
            if os.path.isdir(path):
                package: Package = Package.from_build(path, aur_url)
            elif os.path.exists(path):
                package = Package.from_archive(path, aur_url)
            else:
                package = Package.from_aur(path, aur_url)
            return package
        except InvalidPackageInfo:
            raise
        except Exception as e:
            raise InvalidPackageInfo(str(e))

    def is_outdated(self, remote: Package) -> bool:
        remote_version = remote.actual_version()  # either normal version or updated VCS
        result = check_output('vercmp', self.version, remote_version, exception=None)
        return True if int(result) < 0 else False
