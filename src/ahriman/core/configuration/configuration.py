#
# Copyright (c) 2021-2024 ahriman team.
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

from ahriman.core.configuration.shell_interpolator import ShellInterpolator
from ahriman.core.exceptions import InitializeError
from ahriman.models.repository_id import RepositoryId
from ahriman.models.repository_paths import RepositoryPaths


class Configuration(configparser.RawConfigParser):
    """
    extension for built-in configuration parser

    Attributes:
        ARCHITECTURE_SPECIFIC_SECTIONS(list[str]): (class attribute) known sections which can be architecture specific.
            Required by dump and merging functions
        SYSTEM_CONFIGURATION_PATH(Path): (class attribute) default system configuration path distributed by package
        includes(list[Path]): list of includes which were read
        path(Path | None): path to root configuration file
        repository_id(RepositoryId | None): repository unique identifier

    Examples:
        Configuration class provides additional method in order to handle application configuration. Since this class is
        derived from built-in :class:`configparser.RawConfigParser` class, the same flow is applicable here.
        Nevertheless, it is recommended to use :func:`from_path()` class method which also calls initialization
        methods::

            >>> from pathlib import Path
            >>>
            >>> configuration = Configuration.from_path(Path("/etc/ahriman.ini"), RepositoryId("x86_64", "aur"))
            >>> repository_name = configuration.get("repository", "name")
            >>> makepkg_flags = configuration.getlist("build", "makepkg_flags")

        The configuration instance loaded in this way will contain only sections which are defined for the specified
        architecture according to the merge rules. Moreover, the architecture names will be removed from section names.

        In order to get current settings, the :func:`check_loaded()` method can be used. This method will raise an
        :exc:`ahriman.core.exceptions.InitializeError` in case if configuration was not yet loaded::

            >>> path, repository_id = configuration.check_loaded()
    """

    _LEGACY_ARCHITECTURE_SPECIFIC_SECTIONS = ["web"]
    ARCHITECTURE_SPECIFIC_SECTIONS = ["alpm", "build", "sign"]
    SYSTEM_CONFIGURATION_PATH = Path(sys.prefix) / "share" / "ahriman" / "settings" / "ahriman.ini"
    converters: dict[str, Callable[[str], Any]]  # typing guard

    def __init__(self, allow_no_value: bool = False) -> None:
        """
        Args:
            allow_no_value(bool, optional): copies :class:`configparser.RawConfigParser` behaviour. In case if it is set
                to ``True``, the keys without values will be allowed (Default value = False)
        """
        configparser.RawConfigParser.__init__(
            self,
            allow_no_value=allow_no_value,
            interpolation=ShellInterpolator(),
            converters={
                "list": shlex.split,
                "path": self._convert_path,
                "pathlist": lambda value: [self._convert_path(element) for element in shlex.split(value)],
            }
        )

        self.repository_id: RepositoryId | None = None
        self.path: Path | None = None
        self.includes: list[Path] = []

    @property
    def architecture(self) -> str:
        """
        repository architecture for backward compatibility

        Returns:
            str: repository architecture
        """
        _, repository_id = self.check_loaded()
        return repository_id.architecture

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
        repository name for backward compatibility

        Returns:
            str: repository name
        """
        _, repository_id = self.check_loaded()
        return repository_id.name

    @property
    def repository_paths(self) -> RepositoryPaths:
        """
        construct RepositoryPaths instance based on the configuration

        Returns:
            RepositoryPaths: repository paths instance
        """
        _, repository_id = self.check_loaded()
        return RepositoryPaths(self.getpath("repository", "root"), repository_id)

    @classmethod
    def from_path(cls, path: Path, repository_id: RepositoryId) -> Self:
        """
        constructor with full object initialization

        Args:
            path(Path): path to root configuration file
            repository_id(RepositoryId): repository unique identifier

        Returns:
            Self: configuration instance
        """
        configuration = cls()
        configuration.load(path)
        configuration.merge_sections(repository_id)
        return configuration

    @staticmethod
    def section_name(section: str, *suffixes: str | None) -> str:
        """
        generate section name for sections which depends on context

        Args:
            section(str): section name
            *suffixes(str | None): session suffix, e.g. repository architecture

        Returns:
            str: correct section name for repository specific section
        """
        for suffix in filter(bool, suffixes):
            section = f"{section}:{suffix}"
        return section

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

    def check_loaded(self) -> tuple[Path, RepositoryId]:
        """
        check if service was actually loaded

        Returns:
            tuple[Path, RepositoryId]: configuration root path and architecture if loaded

        Raises:
            InitializeError: in case if architecture and/or path are not set
        """
        if self.path is None or self.repository_id is None:
            raise InitializeError("Configuration path and/or repository id are not set")
        return self.path, self.repository_id

    def dump(self) -> dict[str, dict[str, str]]:
        """
        dump configuration to dictionary

        Returns:
            dict[str, dict[str, str]]: configuration dump for specific architecture
        """
        return {
            section: dict(self.items(section))
            for section in self.sections()
        }

    # pylint and mypy are too stupid to find these methods
    # pylint: disable=missing-function-docstring,unused-argument
    def getlist(self, *args: Any, **kwargs: Any) -> list[str]: ...  # type: ignore[empty-body]

    def getpath(self, *args: Any, **kwargs: Any) -> Path: ...  # type: ignore[empty-body]

    def getpathlist(self, *args: Any, **kwargs: Any) -> list[Path]: ...  # type: ignore[empty-body]

    def gettype(self, section: str, repository_id: RepositoryId, *, fallback: str | None = None) -> tuple[str, str]:
        """
        get type variable with fallback to old logic. Despite the fact that it has same semantics as other get* methods,
        but it has different argument list

        Args:
            section(str): section name
            repository_id(RepositoryId): repository unique identifier
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
        for specific in self.override_sections(section, repository_id):
            if self.has_section(specific):
                return specific, section
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
        self.load_includes()  # load includes

    def load_includes(self, path: Path | None = None) -> None:
        """
        load configuration includes from specified path

        Args:
            path(Path | None, optional): path to directory with include files. If none set, the default path will be
                used (Default value = None)
        """
        self.includes = []  # reset state

        try:
            path = path or self.include
            for include in sorted(path.glob("*.ini")):
                if include == self.logging_path:
                    continue  # we don't want to load logging explicitly
                self.read(include)
                self.includes.append(include)
        except (FileNotFoundError, configparser.NoOptionError, configparser.NoSectionError):
            pass

    def merge_sections(self, repository_id: RepositoryId) -> None:
        """
        merge architecture and repository specific sections into main configuration

        Args:
            repository_id(RepositoryId): repository unique identifier
        """
        self.repository_id = repository_id

        for section in self.ARCHITECTURE_SPECIFIC_SECTIONS + self._LEGACY_ARCHITECTURE_SPECIFIC_SECTIONS:
            for specific in self.override_sections(section, repository_id):
                if self.has_section(specific):
                    # if there is no such section it means that there is no overrides for this arch,
                    # but we anyway will have to delete sections for others architectures
                    for key, value in self[specific].items():
                        self.set_option(section, key, value)

            # remove any arch/repo specific section
            for foreign in self.sections():
                # we would like to use lambda filter here, but pylint is too dumb
                if not foreign.startswith(f"{section}:"):
                    continue
                self.remove_section(foreign)

    def override_sections(self, section: str, repository_id: RepositoryId) -> list[str]:
        """
        extract override sections

        Args:
            section(str): section name
            repository_id(RepositoryId): repository unique identifier

        Returns:
            list[str]: architecture and repository specific sections in correct order
        """
        if repository_id.is_empty:  # special case, guess sections from configuration
            return sorted(specific for specific in self.sections() if specific.startswith(f"{section}:"))
        # the valid order is global < per architecture < per repository < per repository and architecture
        return [
            Configuration.section_name(section, repository_id.architecture),  # architecture specific override
            Configuration.section_name(section, repository_id.name),  # override with repository name
            Configuration.section_name(section, repository_id.name, repository_id.architecture),  # both
        ]

    def reload(self) -> None:
        """
        reload configuration if possible or raise exception otherwise
        """
        path, repository_id = self.check_loaded()
        for section in self.sections():  # clear current content
            self.remove_section(section)
        self.load(path)
        self.merge_sections(repository_id)

    def set_option(self, section: str, option: str, value: str) -> None:
        """
        set option. Unlike default :func:`configparser.RawConfigParser.set()` it also creates section if
        it does not exist

        Args:
            section(str): section name
            option(str): option name
            value(str): option value as string in parsable format
        """
        if not self.has_section(section):
            self.add_section(section)
        self.set(section, option, value)
