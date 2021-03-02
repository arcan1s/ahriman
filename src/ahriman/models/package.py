from __future__ import annotations

import aur
import os

from configparser import RawConfigParser
from dataclasses import dataclass
from srcinfo.parse import parse_srcinfo
from typing import Type

from ahriman.core.exceptions import InvalidPackageInfo
from ahriman.core.util import check_output


@dataclass
class Package:
    name: str
    version: str
    url: str

    @property
    def is_multilib(self) -> bool:
        return self.name.startswith('lib32-')

    @classmethod
    def from_archive(cls: Type[Package], path: str, aur_url: str) -> Package:
        name, version = check_output('expac', '-p', '%n %v', path, exception=None).split()
        return cls(name, version, f'{aur_url}/{name}.git')

    @classmethod
    def from_aur(cls: Type[Package], name: str, aur_url: str)-> Package:
        package = aur.info(name)
        return cls(package.name, package.version, f'{aur_url}/{name}.git')

    @classmethod
    def from_build(cls: Type[Package], path: str) -> Package:
        git_config = RawConfigParser()
        git_config.read(os.path.join(path, '.git', 'config'))

        with open(os.path.join(path, '.SRCINFO')) as fn:
            src_info, errors = parse_srcinfo(fn.read())
        if errors:
            raise InvalidPackageInfo(errors)

        return cls(src_info['pkgbase'], f'{src_info["pkgver"]}-{src_info["pkgrel"]}',
                   git_config.get('remote "origin"', 'url'))

    @classmethod
    def load(cls: Type[Package], path: str, aur_url: str) -> Package:
        try:
            if os.path.isdir(path):
                package: Package = cls.from_build(path)
            elif os.path.exists(path):
                package = cls.from_archive(path, aur_url)
            else:
                package = cls.from_aur(path, aur_url)
            return package
        except InvalidPackageInfo:
            raise
        except Exception as e:
            raise InvalidPackageInfo(str(e))

    def is_outdated(self, remote: Package) -> bool:
        result = check_output('vercmp', self.version, remote.version, exception=None)
        return True if int(result) < 0 else False