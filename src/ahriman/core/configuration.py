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

import configparser
import logging

from logging.config import fileConfig
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar


T = TypeVar("T")


class Configuration(configparser.RawConfigParser):
    """
    extension for built-in configuration parser
    :ivar path: path to root configuration file
    :cvar ARCHITECTURE_SPECIFIC_SECTIONS: known sections which can be architecture specific (required by dump)
    :cvar DEFAULT_LOG_FORMAT: default log format (in case of fallback)
    :cvar DEFAULT_LOG_LEVEL: default log level (in case of fallback)
    :cvar STATIC_SECTIONS: known sections which are not architecture specific (required by dump)
    """

    DEFAULT_LOG_FORMAT = "[%(levelname)s %(asctime)s] [%(filename)s:%(lineno)d] [%(funcName)s]: %(message)s"
    DEFAULT_LOG_LEVEL = logging.DEBUG

    STATIC_SECTIONS = ["alpm", "report", "repository", "settings", "upload"]
    ARCHITECTURE_SPECIFIC_SECTIONS = ["build", "html", "rsync", "s3", "sign", "web"]

    def __init__(self) -> None:
        """
        default constructor. In the most cases must not be called directly
        """
        configparser.RawConfigParser.__init__(self, allow_no_value=True)
        self.path: Optional[Path] = None

    @property
    def include(self) -> Path:
        """
        :return: path to directory with configuration includes
        """
        return self.getpath("settings", "include")

    @classmethod
    def from_path(cls: Type[Configuration], path: Path, logfile: bool) -> Configuration:
        """
        constructor with full object initialization
        :param path: path to root configuration file
        :param logfile: use log file to output messages
        :return: configuration instance
        """
        config = cls()
        config.load(path)
        config.load_logging(logfile)
        return config

    @staticmethod
    def section_name(section: str, architecture: str) -> str:
        """
        generate section name for architecture specific sections
        :param section: section name
        :param architecture: repository architecture
        :return: correct section name for repository specific section
        """
        return f"{section}_{architecture}"

    def dump(self, architecture: str) -> Dict[str, Dict[str, str]]:
        """
        dump configuration to dictionary
        :param architecture: repository architecture
        :return: configuration dump for specific architecture
        """
        result: Dict[str, Dict[str, str]] = {}
        for section in Configuration.STATIC_SECTIONS:
            if not self.has_section(section):
                continue
            result[section] = dict(self[section])
        for section in Configuration.ARCHITECTURE_SPECIFIC_SECTIONS:
            # get global settings
            settings = dict(self[section]) if self.has_section(section) else {}
            # get overrides
            specific = self.section_name(section, architecture)
            specific_settings = dict(self[specific]) if self.has_section(specific) else {}
            # merge
            settings.update(specific_settings)
            if settings:  # append only in case if it is not empty
                result[section] = settings

        return result

    def getlist(self, section: str, key: str) -> List[str]:
        """
        get space separated string list option
        :param section: section name
        :param key: key name
        :return: list of string if option is set, empty list otherwise
        """
        raw = self.get(section, key, fallback=None)
        if not raw:  # empty string or none
            return []
        return raw.split()

    def getpath(self, section: str, key: str) -> Path:
        """
        helper to generate absolute configuration path for relative settings value
        :param section: section name
        :param key: key name
        :return: absolute path according to current path configuration
        """
        value = Path(self.get(section, key))
        if self.path is None or value.is_absolute():
            return value
        return self.path.parent / value

    def load(self, path: Path) -> None:
        """
        fully load configuration
        :param path: path to root configuration file
        """
        self.path = path
        self.read(self.path)
        self.load_includes()

    def load_includes(self) -> None:
        """
        load configuration includes
        """
        try:
            for path in sorted(self.include.glob("*.ini")):
                self.read(path)
        except (FileNotFoundError, configparser.NoOptionError):
            pass

    def load_logging(self, logfile: bool) -> None:
        """
        setup logging settings from configuration
        :param logfile: use log file to output messages
        """
        def file_logger() -> None:
            try:
                config_path = self.getpath("settings", "logging")
                fileConfig(config_path)
            except (FileNotFoundError, PermissionError):
                console_logger()
                logging.exception("could not create logfile, fallback to stderr")

        def console_logger() -> None:
            logging.basicConfig(filename=None, format=Configuration.DEFAULT_LOG_FORMAT,
                                level=Configuration.DEFAULT_LOG_LEVEL)

        if logfile:
            file_logger()
        else:
            console_logger()

    def wrap(self, section: str, architecture: str, key: str, function: Callable[..., T], **kwargs: Any) -> T:
        """
        wrapper to get option by either using architecture specific section or generic section
        :param section: section name
        :param architecture: repository architecture
        :param key: key name
        :param function: function to call, e.g. `Configuration.get`
        :param kwargs: any other keywords which will be passed to function directly
        :return: either value from architecture specific section or global value
        """
        specific_section = self.section_name(section, architecture)
        if self.has_option(specific_section, key):
            return function(specific_section, key, **kwargs)
        return function(section, key, **kwargs)
