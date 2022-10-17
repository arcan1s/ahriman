#
# Copyright (c) 2021-2022 ahriman team.
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
import sys

from logging.config import fileConfig
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple, Type

from ahriman.core.exceptions import InitializeException
from ahriman.models.repository_paths import RepositoryPaths


class Configuration(configparser.RawConfigParser):
    """
    extension for built-in configuration parser

    Attributes:
        ARCHITECTURE_SPECIFIC_SECTIONS(List[str]): (class attribute) known sections which can be architecture specific.
            Required by dump and merging functions
        DEFAULT_LOG_FORMAT(str): (class attribute) default log format (in case of fallback)
        DEFAULT_LOG_LEVEL(int): (class attribute) default log level (in case of fallback)
        SYSTEM_CONFIGURATION_PATH(Path): (class attribute) default system configuration path distributed by package
        architecture(Optional[str]): repository architecture
        path(Optional[Path]): path to root configuration file

    Examples:
        Configuration class provides additional method in order to handle application configuration. Since this class is
        derived from built-in ``configparser.RawConfigParser`` class, the same flow is applicable here. Nevertheless,
        it is recommended to use ``from_path`` class method which also calls initialization methods::

            >>> from pathlib import Path
            >>>
            >>> configuration = Configuration.from_path(Path("/etc/ahriman.ini"), "x86_64", quiet=False)
            >>> repository_name = configuration.get("repository", "name")
            >>> makepkg_flags = configuration.getlist("build", "makepkg_flags")

        The configuration instance loaded in this way will contain only sections which are defined for the specified
        architecture according to the merge rules. Moreover, the architecture names will be removed from section names.

        In order to get current settings, the ``check_loaded`` method can be used. This method will raise an
        ``InitializeException`` in case if configuration was not yet loaded::

            >>> path, architecture = configuration.check_loaded()
    """

    DEFAULT_LOG_FORMAT = "[%(levelname)s %(asctime)s] [%(filename)s:%(lineno)d %(funcName)s]: %(message)s"
    DEFAULT_LOG_LEVEL = logging.DEBUG

    ARCHITECTURE_SPECIFIC_SECTIONS = ["build", "sign", "web"]
    SYSTEM_CONFIGURATION_PATH = Path(sys.prefix) / "share" / "ahriman" / "settings" / "ahriman.ini"

    def __init__(self, allow_no_value: bool = False) -> None:
        """
        default constructor. In the most cases must not be called directly

        Args:
            allow_no_value(bool): copies ``configparser.RawConfigParser`` behaviour. In case if it is set to ``True``,
                the keys without values will be allowed
        """
        configparser.RawConfigParser.__init__(self, allow_no_value=allow_no_value, converters={
            "list": self.__convert_list,
            "path": self.__convert_path,
        })
        self.architecture: Optional[str] = None
        self.path: Optional[Path] = None

    @property
    def include(self) -> Path:
        """
        get full path to include directory

        Returns:
            Path: path to directory with configuration includes
        """
        return self.getpath("settings", "include")

    @property
    def logging_path(self) -> Path:
        """
        get full path to logging configuration

        Returns:
            Path: path to logging configuration
        """
        return self.getpath("settings", "logging")

    @property
    def repository_paths(self) -> RepositoryPaths:
        """
        construct RepositoryPaths instance based on the configuration

        Returns:
            RepositoryPaths: repository paths instance
        """
        _, architecture = self.check_loaded()
        return RepositoryPaths(self.getpath("repository", "root"), architecture)

    @classmethod
    def from_path(cls: Type[Configuration], path: Path, architecture: str, quiet: bool) -> Configuration:
        """
        constructor with full object initialization

        Args:
            path(Path): path to root configuration file
            architecture(str): repository architecture
            quiet(bool): force disable any log messages

        Returns:
            Configuration: configuration instance
        """
        configuration = cls()
        configuration.load(path)
        configuration.merge_sections(architecture)
        configuration.load_logging(quiet)
        return configuration

    @staticmethod
    def __convert_list(value: str) -> List[str]:
        """
        convert string value to list of strings

        Args:
            value(str): string configuration value

        Returns:
            List[str]: list of string from the parsed string

        Raises:
            ValueError: in case if option value contains unclosed quotes
        """
        def generator() -> Generator[str, None, None]:
            quote_mark = None
            word = ""
            for char in value:
                if char in ("'", "\"") and quote_mark is None:  # quoted part started, store quote and do nothing
                    quote_mark = char
                elif char == quote_mark:  # quoted part ended, reset quotation
                    quote_mark = None
                elif char == " " and quote_mark is None:  # found space outside the quotation, yield the word
                    yield word
                    word = ""
                else:  # append character to the buffer
                    word += char
            if quote_mark:  # there is unmatched quote
                raise ValueError(f"unmatched quote in {value}")
            yield word  # sequence done, return whatever we found

        return [word for word in generator() if word]

    @staticmethod
    def section_name(section: str, suffix: str) -> str:
        """
        generate section name for sections which depends on context

        Args:
            section(str): section name
            suffix(str): session suffix, e.g. repository architecture

        Returns:
            str: correct section name for repository specific section
        """
        return f"{section}:{suffix}"

    def __convert_path(self, value: str) -> Path:
        """
        convert string value to path object

        Args:
            value(str): string configuration value

        Returns:
            Path: path object which represents the configuration value
        """
        path = Path(value)
        if self.path is None or path.is_absolute():
            return path
        return self.path.parent / path

    def check_loaded(self) -> Tuple[Path, str]:
        """
        check if service was actually loaded

        Returns:
            Tuple[Path, str]: configuration root path and architecture if loaded

        Raises:
            InitializeException: in case if architecture and/or path are not set
        """
        if self.path is None or self.architecture is None:
            raise InitializeException("Configuration path and/or architecture are not set")
        return self.path, self.architecture

    def dump(self) -> Dict[str, Dict[str, str]]:
        """
        dump configuration to dictionary

        Returns:
            Dict[str, Dict[str, str]]: configuration dump for specific architecture
        """
        return {
            section: dict(self[section])
            for section in self.sections()
        }

    # pylint and mypy are too stupid to find these methods
    # pylint: disable=missing-function-docstring,multiple-statements,unused-argument
    def getlist(self, *args: Any, **kwargs: Any) -> List[str]: ...

    def getpath(self, *args: Any, **kwargs: Any) -> Path: ...

    def gettype(self, section: str, architecture: str) -> Tuple[str, str]:
        """
        get type variable with fallback to old logic
        Despite the fact that it has same semantics as other get* methods, but it has different argument list

        Args:
            section(str): section name
            architecture(str): repository architecture

        Returns:
            Tuple[str, str]: section name and found type name

        Raises:
            configparser.NoSectionError: in case if no section found
        """
        group_type = self.get(section, "type", fallback=None)  # new-style logic
        if group_type is not None:
            return section, group_type
        # okay lets check for the section with architecture name
        full_section = self.section_name(section, architecture)
        if self.has_section(full_section):
            return full_section, section
        # okay lets just use section as type
        if not self.has_section(section):
            raise configparser.NoSectionError(section)
        return section, section

    def load(self, path: Path) -> None:
        """
        fully load configuration

        Args:
            path(Path): path to root configuration file
        """
        if not path.is_file():  # fallback to the system file
            path = self.SYSTEM_CONFIGURATION_PATH
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

    def load_logging(self, quiet: bool) -> None:
        """
        setup logging settings from configuration

        Args:
            quiet(bool): force disable any log messages
        """
        try:
            path = self.logging_path
            fileConfig(path)
        except Exception:
            logging.basicConfig(filename=None, format=self.DEFAULT_LOG_FORMAT,
                                level=self.DEFAULT_LOG_LEVEL)
            logging.exception("could not load logging from configuration, fallback to stderr")
        if quiet:
            logging.disable(logging.WARNING)  # only print errors here

    def merge_sections(self, architecture: str) -> None:
        """
        merge architecture specific sections into main configuration

        Args:
            architecture(str): repository architecture
        """
        self.architecture = architecture
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

    def reload(self) -> None:
        """
        reload configuration if possible or raise exception otherwise
        """
        path, architecture = self.check_loaded()
        for section in self.sections():  # clear current content
            self.remove_section(section)
        self.load(path)
        self.merge_sections(architecture)

    def set_option(self, section: str, option: str, value: Optional[str]) -> None:
        """
        set option. Unlike default ``configparser.RawConfigParser.set`` it also creates section if it does not exist

        Args:
            section(str): section name
            option(str): option name
            value(Optional[str]): option value as string in parsable format
        """
        if not self.has_section(section):
            self.add_section(section)
        self.set(section, option, value)
