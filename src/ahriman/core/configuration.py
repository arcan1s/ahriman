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

import configparser
import os

from logging.config import fileConfig
from typing import List, Optional, Type


# built-in configparser extension
class Configuration(configparser.RawConfigParser):

    def __init__(self) -> None:
        configparser.RawConfigParser.__init__(self, allow_no_value=True)
        self.path: Optional[str] = None

    @property
    def include(self) -> str:
        return self.get('settings', 'include')

    @classmethod
    def from_path(cls: Type[Configuration], path: str) -> Configuration:
        config = cls()
        config.load(path)
        config.load_logging()
        return config

    def getlist(self, section: str, key: str) -> List[str]:
        raw = self.get(section, key, fallback=None)
        if not raw:  # empty string or none
            return []
        return raw.split()

    def get_section_name(self, prefix: str, suffix: str) -> str:
        probe = f'{prefix}_{suffix}'
        return probe if self.has_section(probe) else prefix

    def load(self, path: str) -> None:
        self.path = path
        self.read(self.path)
        self.load_includes()

    def load_includes(self) -> None:
        try:
            for conf in filter(lambda p: p.endswith('.ini'), sorted(os.listdir(self.include))):
                self.read(os.path.join(self.include, conf))
        except (FileNotFoundError, configparser.NoOptionError):
            pass

    def load_logging(self) -> None:
        fileConfig(self.get('settings', 'logging'))
