#
# Copyright (c) 2021-2025 ahriman team.
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
from collections.abc import Callable
from typing import ClassVar

from ahriman.core.configuration import Configuration
from ahriman.core.configuration.schema import ConfigurationSchema
from ahriman.core.log import LazyLogging
from ahriman.models.package import Package
from ahriman.models.repository_id import RepositoryId
from ahriman.models.result import Result


class Trigger(LazyLogging):
    """
    trigger base class

    Attributes:
        CONFIGURATION_SCHEMA(ConfigurationSchema): (class attribute) configuration schema template
        CONFIGURATION_SCHEMA_FALLBACK(str | None): (class attribute) optional fallback option for defining
            configuration schema type used
        configuration(Configuration): configuration instance
        repository_id(RepositoryId): repository unique identifier

    Examples:
        This class must be used in order to create own extension. Basically idea is the following::

            >>> class CustomTrigger(Trigger):
            >>>     def on_result(self, result: Result, packages: list[Package]) -> None:
            >>>         perform_some_action()

        Having this class you can pass it to ``configuration`` and it will be run on action::

            >>> from ahriman.core.triggers import TriggerLoader
            >>>
            >>> configuration = Configuration()
            >>> configuration.set_option("build", "triggers", "my.awesome.package.CustomTrigger")
            >>>
            >>> loader = TriggerLoader.load(RepositoryId("x86_64", "aur"), configuration)
            >>> loader.on_result(Result(), [])
    """

    CONFIGURATION_SCHEMA: ClassVar[ConfigurationSchema] = {}
    CONFIGURATION_SCHEMA_FALLBACK: ClassVar[str | None] = None

    def __init__(self, repository_id: RepositoryId, configuration: Configuration) -> None:
        """
        Args:
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
        """
        self.repository_id = repository_id
        self.configuration = configuration

    @property
    def architecture(self) -> str:
        """
        repository architecture for backward compatibility

        Returns:
            str: repository architecture
        """
        return self.repository_id.architecture

    @classmethod
    def configuration_schema(cls, configuration: Configuration | None) -> ConfigurationSchema:
        """
        configuration schema based on supplied service configuration

        Notes:
            Schema must be in cerberus format, for details and examples you can check built-in triggers.

        Args:
            configuration(Configuration | None): configuration instance. If set to None, the default schema
                should be returned

        Returns:
            ConfigurationSchema: configuration schema in cerberus format
        """
        if configuration is None:
            return cls.CONFIGURATION_SCHEMA

        result: ConfigurationSchema = {}
        for target in cls.configuration_sections(configuration):
            for section in configuration.sections():
                if not (section == target or section.startswith(f"{target}:")):
                    # either repository specific or exact name
                    continue
                schema_name = configuration.get(section, "type", fallback=section)

                if schema_name not in cls.CONFIGURATION_SCHEMA:
                    continue
                result[section] = cls.CONFIGURATION_SCHEMA[schema_name]

        return result

    @classmethod
    def configuration_sections(cls, configuration: Configuration) -> list[str]:
        """
        extract configuration sections from configuration

        Args:
            configuration(Configuration): configuration instance

        Returns:
            list[str]: read configuration sections belong to this trigger

        Examples:
            This method can be used in order to extract specific configuration sections which are set by user, e.g.
            from sources::

                >>> @classmethod
                >>> def configuration_sections(cls, configuration: Configuration) -> list[str]:
                >>>     return configuration.getlist("report", "target", fallback=[])
        """
        del configuration
        return []

    def on_result(self, result: Result, packages: list[Package]) -> None:
        """
        trigger action which will be called after build process with process result

        Args:
            result(Result): build result
            packages(list[Package]): list of all available packages
        """
        # compatibility with old triggers
        run: Callable[[Result, list[Package]], None] | None = getattr(self, "run", None)
        if run is not None:
            run(result, packages)

    def on_start(self) -> None:
        """
        trigger action which will be called at the start of the application
        """

    def on_stop(self) -> None:
        """
        trigger action which will be called before the stop of the application
        """
