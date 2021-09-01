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
from typing import Dict, List, Optional, Type


class Configuration(configparser.RawConfigParser):
    """
    extension for built-in configuration parser
    :ivar path: path to root configuration file
    :cvar ARCHITECTURE_SPECIFIC_SECTIONS: known sections which can be architecture specific (required by dump)
    :cvar DEFAULT_LOG_FORMAT: default log format (in case of fallback)
    :cvar DEFAULT_LOG_LEVEL: default log level (in case of fallback)
    """

    DEFAULT_LOG_FORMAT = "[%(levelname)s %(asctime)s] [%(filename)s:%(lineno)d] [%(funcName)s]: %(message)s"
    DEFAULT_LOG_LEVEL = logging.DEBUG

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

    @property
    def logging_path(self) -> Path:
        """
        :return: path to logging configuration
        """
        return self.getpath("settings", "logging")

    @classmethod
    def from_path(cls: Type[Configuration], path: Path, architecture: str, logfile: bool) -> Configuration:
        """
        constructor with full object initialization
        :param path: path to root configuration file
        :param architecture: repository architecture
        :param logfile: use log file to output messages
        :return: configuration instance
        """
        config = cls()
        config.load(path)
        config.merge_sections(architecture)
        config.load_logging(logfile)
        return config

    @staticmethod
    def section_name(section: str, suffix: str) -> str:
        """
        generate section name for sections which depends on context
        :param section: section name
        :param suffix: session suffix, e.g. repository architecture
        :return: correct section name for repository specific section
        """
        return f"{section}:{suffix}"

    def dump(self) -> Dict[str, Dict[str, str]]:
        """
        dump configuration to dictionary
        :return: configuration dump for specific architecture
        """
        return {
            section: dict(self[section])
            for section in self.sections()
        }

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
                if path == self.logging_path:
                    continue  # we don't want to load logging explicitly
                self.read(path)
        except (FileNotFoundError, configparser.NoOptionError, configparser.NoSectionError):
            pass

    def load_logging(self, logfile: bool) -> None:
        """
        setup logging settings from configuration
        :param logfile: use log file to output messages
        """
        def file_logger() -> None:
            try:
                path = self.logging_path
                fileConfig(path)
            except (FileNotFoundError, PermissionError):
                console_logger()
                logging.exception("could not create logfile, fallback to stderr")

        def console_logger() -> None:
            logging.basicConfig(filename=None, format=self.DEFAULT_LOG_FORMAT,
                                level=self.DEFAULT_LOG_LEVEL)

        if logfile:
            file_logger()
        else:
            console_logger()

    def merge_sections(self, architecture: str) -> None:
        """
        merge architecture specific sections into main configuration
        :param architecture: repository architecture
        """
        for section in self.ARCHITECTURE_SPECIFIC_SECTIONS:
            # get overrides
            specific = self.section_name(section, architecture)
            if self.has_section(specific):
                # if there is no such section it means that there is no overrides for this arch
                # but we anyway will have to delete sections for others archs
                for key, value in self[specific].items():
                    self.set_option(section, key, value)
            # remove any arch specific section
            for foreign in self.sections():
                # we would like to use lambda filter here, but pylint is too dumb
                if not foreign.startswith(f"{section}:"):
                    continue
                self.remove_section(foreign)

    def set_option(self, section: str, option: str, value: Optional[str]) -> None:
        """
        set option. Unlike default `configparser.RawConfigParser.set` it also creates section if it does not exist
        :param section: section name
        :param option: option name
        :param value: option value as string in parsable format
        """
        if not self.has_section(section):
            self.add_section(section)
        self.set(section, option, value)
