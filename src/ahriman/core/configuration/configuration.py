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
import configparser
import shlex
import sys

from collections.abc import Callable
from pathlib import Path
from typing import Any, Self

from ahriman.core.exceptions import InitializeError
from ahriman.models.repository_paths import RepositoryPaths


class Configuration(configparser.RawConfigParser):
    """
    extension for built-in configuration parser

    Attributes:
        ARCHITECTURE_SPECIFIC_SECTIONS(list[str]): (class attribute) known sections which can be architecture specific.
            Required by dump and merging functions
        SYSTEM_CONFIGURATION_PATH(Path): (class attribute) default system configuration path distributed by package
        architecture(str | None): repository architecture
        includes(list[Path]): list of includes which were read
        path(Path | None): path to root configuration file

    Examples:
        Configuration class provides additional method in order to handle application configuration. Since this class is
        derived from built-in ``configparser.RawConfigParser`` class, the same flow is applicable here. Nevertheless,
        it is recommended to use ``from_path`` class method which also calls initialization methods::

            >>> from pathlib import Path
            >>>
            >>> configuration = Configuration.from_path(Path("/etc/ahriman.ini"), "x86_64")
            >>> repository_name = configuration.get("repository", "name")
            >>> makepkg_flags = configuration.getlist("build", "makepkg_flags")

        The configuration instance loaded in this way will contain only sections which are defined for the specified
        architecture according to the merge rules. Moreover, the architecture names will be removed from section names.

        In order to get current settings, the ``check_loaded`` method can be used. This method will raise an
        ``InitializeError`` in case if configuration was not yet loaded::

            >>> path, architecture = configuration.check_loaded()
    """

    ARCHITECTURE_SPECIFIC_SECTIONS = ["alpm", "build", "sign", "web"]
    SYSTEM_CONFIGURATION_PATH = Path(sys.prefix) / "share" / "ahriman" / "settings" / "ahriman.ini"
    converters: dict[str, Callable[[str], Any]]  # typing guard

    def __init__(self, allow_no_value: bool = False) -> None:
        """
        default constructor. In the most cases must not be called directly

        Args:
            allow_no_value(bool, optional): copies ``configparser.RawConfigParser`` behaviour. In case if it is set
                to ``True``, the keys without values will be allowed (Default value = False)
        """
        configparser.RawConfigParser.__init__(self, allow_no_value=allow_no_value, converters={
            "list": shlex.split,
            "path": self._convert_path,
        })
        self.architecture: str | None = None
        self.path: Path | None = None
        self.includes: list[Path] = []

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
    def repository_name(self) -> str:
        """
        repository name as defined by configuration

        Returns:
            str: repository name from configuration
        """
        return self.get("repository", "name")

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
    def from_path(cls, path: Path, architecture: str) -> Self:
        """
        constructor with full object initialization

        Args:
            path(Path): path to root configuration file
            architecture(str): repository architecture

        Returns:
            Self: configuration instance
        """
        configuration = cls()
        configuration.load(path)
        configuration.merge_sections(architecture)
        return configuration

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

    def _convert_path(self, value: str) -> Path:
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

    def check_loaded(self) -> tuple[Path, str]:
        """
        check if service was actually loaded

        Returns:
            tuple[Path, str]: configuration root path and architecture if loaded

        Raises:
            InitializeError: in case if architecture and/or path are not set
        """
        if self.path is None or self.architecture is None:
            raise InitializeError("Configuration path and/or architecture are not set")
        return self.path, self.architecture

    def dump(self) -> dict[str, dict[str, str]]:
        """
        dump configuration to dictionary

        Returns:
            dict[str, dict[str, str]]: configuration dump for specific architecture
        """
        return {
            section: dict(self[section])
            for section in self.sections()
        }

    # pylint and mypy are too stupid to find these methods
    # pylint: disable=missing-function-docstring,unused-argument
    def getlist(self, *args: Any, **kwargs: Any) -> list[str]: ...  # type: ignore[empty-body]

    def getpath(self, *args: Any, **kwargs: Any) -> Path: ...  # type: ignore[empty-body]

    def gettype(self, section: str, architecture: str, *, fallback: str | None = None) -> tuple[str, str]:
        """
        get type variable with fallback to old logic. Despite the fact that it has same semantics as other get* methods,
        but it has different argument list

        Args:
            section(str): section name
            architecture(str): repository architecture
            fallback(str | None, optional): optional fallback type if any. If set, second element of the tuple will
                be always set to this value (Default value = None)

        Returns:
            tuple[str, str]: section name and found type name

        Raises:
            configparser.NoSectionError: in case if no section found
        """
        if (group_type := self.get(section, "type", fallback=fallback)) is not None:
            return section, group_type  # new-style logic
        # okay lets check for the section with architecture name
        full_section = self.section_name(section, architecture)
        if self.has_section(full_section):
            return full_section, section
        # okay lets just use section as type
        if self.has_section(section):
            return section, section
        raise configparser.NoSectionError(section)

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
        self.includes = []  # reset state
        try:
            for path in sorted(self.include.glob("*.ini")):
                if path == self.logging_path:
                    continue  # we don't want to load logging explicitly
                self.read(path)
                self.includes.append(path)
        except (FileNotFoundError, configparser.NoOptionError, configparser.NoSectionError):
            pass

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
                # if there is no such section it means that there is no overrides for this arch,
                # but we anyway will have to delete sections for others architectures
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

    def set_option(self, section: str, option: str, value: str) -> None:
        """
        set option. Unlike default ``configparser.RawConfigParser.set`` it also creates section if it does not exist

        Args:
            section(str): section name
            option(str): option name
            value(str): option value as string in parsable format
        """
        if not self.has_section(section):
            self.add_section(section)
        self.set(section, option, value)
