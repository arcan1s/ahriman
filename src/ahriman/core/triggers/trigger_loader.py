#
# Copyright (c) 2021-2026 ahriman team.
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
import atexit
import contextlib
import os

from collections.abc import Generator
from importlib import import_module, machinery
from pathlib import Path
from types import ModuleType
from typing import Self

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import ExtensionError
from ahriman.core.log import LazyLogging
from ahriman.core.triggers import Trigger
from ahriman.models.package import Package
from ahriman.models.repository_id import RepositoryId
from ahriman.models.result import Result


class TriggerLoader(LazyLogging):
    """
    trigger loader class

    Attributes:
        triggers(list[Trigger]): list of loaded triggers according to the configuration

    Examples:
        This class more likely must not be used directly, but the usual workflow is the following::

            >>> configuration = Configuration()  # create configuration
            >>> configuration.set_option("build", "triggers", "ahriman.core.report.ReportTrigger")  # set class for load

        Having such configuration you can create instance of the loader::

            >>> loader = TriggerLoader.load(RepositoryId("x86_64", "aur"), configuration)
            >>> print(loader.triggers)

        After that you are free to run triggers::

            >>> loader.on_result(Result(), [])
    """

    def __init__(self) -> None:
        """"""
        self.triggers: list[Trigger] = []

    @classmethod
    def load(cls, repository_id: RepositoryId, configuration: Configuration) -> Self:
        """
        create instance from configuration

        Args:
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance

        Returns:
            Self: fully loaded trigger instance
        """
        instance = cls()
        instance.triggers = [
            trigger
            for trigger_name in instance.selected_triggers(configuration)
            if (trigger := instance.load_trigger(trigger_name, repository_id, configuration)).is_allowed_to_run
        ]

        return instance

    @staticmethod
    def known_triggers(configuration: Configuration) -> list[str]:
        """
        read configuration and return list of known triggers. Unlike :func:`selected_triggers()` this option is used
        mainly for configuration and validation and mentioned triggers are not being executed automatically

        Args:
            configuration(Configuration): configuration instance

        Returns:
            list[str]: list of registered, but not enabled, triggers
        """
        return configuration.getlist("build", "triggers_known", fallback=[])

    @staticmethod
    def selected_triggers(configuration: Configuration) -> list[str]:
        """
        read configuration and return triggers which are set by settings

        Args:
            configuration(Configuration): configuration instance

        Returns:
            list[str]: list of triggers according to configuration
        """
        return configuration.getlist("build", "triggers", fallback=[])

    @contextlib.contextmanager
    def __execute_trigger(self, trigger: Trigger) -> Generator[None, None, None]:
        """
        decorator for calling triggers

        Args:
            trigger(Trigger): trigger instance to be called
        """
        trigger_name = type(trigger).__name__

        try:
            self.logger.info("executing extension %s", trigger_name)
            yield
        except Exception:
            self.logger.exception("got exception while run trigger %s", trigger_name)

    def _load_module_from_file(self, module_path: str, implementation: str) -> ModuleType:
        """
        load module by given file path

        Args:
            module_path(str): import package
            implementation(str): specific trigger implementation, class name, required by import

        Returns:
            ModuleType: module loaded from the imported file
        """
        self.logger.info("load module %s from path %s", implementation, module_path)
        # basically this method is called only if ``module_path`` exists and is file.
        # Thus, this method should never throw :exc:`FileNotFoundError` exception
        loader = machinery.SourceFileLoader(implementation, module_path)
        module = ModuleType(loader.name)
        loader.exec_module(module)

        return module

    def _load_module_from_package(self, package: str) -> ModuleType:
        """
        load module by given package name

        Args:
            package(str): package name to import

        Returns:
            ModuleType: module loaded from the imported module

        Raises:
            ExtensionError: in case if module cannot be loaded from specified package
        """
        self.logger.info("load module from package %s", package)
        try:
            return import_module(package)
        except ModuleNotFoundError:
            raise ExtensionError(f"Module {package} not found") from None

    def load_trigger(self, module_path: str, repository_id: RepositoryId, configuration: Configuration) -> Trigger:
        """
        load trigger by module path

        Args:
            module_path(str): module import path to load
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance

        Returns:
            Trigger: loaded trigger based on settings

        Raises:
            ExtensionError: in case if trigger could not be instantiated
        """
        trigger_type = self.load_trigger_class(module_path)
        try:
            trigger = trigger_type(repository_id, configuration)
        except Exception as ex:
            raise ExtensionError(f"Could not load trigger from {trigger_type} loaded from {module_path}") from ex

        return trigger

    def load_trigger_class(self, module_path: str) -> type[Trigger]:
        """
        load trigger class by module path

        Args:
            module_path(str): module import path to load

        Returns:
            type[Trigger]: loaded trigger type by module path

        Raises:
            ExtensionError: in case if module cannot be loaded from the specified module path or is not a trigger
        """
        def is_readable_file(path: Path) -> bool:
            return os.access(path, os.R_OK) and path.is_file()

        package_or_path, class_name = module_path.rsplit(".", maxsplit=1)

        # it works for both missing permission and file does not exist
        path_like = Path(package_or_path)
        if is_readable_file(path_like):
            module = self._load_module_from_file(package_or_path, class_name)
        elif is_readable_file(path_like.with_suffix(".py")):
            module = self._load_module_from_file(f"{package_or_path}.py", class_name)
        else:
            module = self._load_module_from_package(package_or_path)

        trigger_type = getattr(module, class_name, None)
        if not isinstance(trigger_type, type):
            raise ExtensionError(f"{class_name} of {package_or_path} is not a type")
        if not issubclass(trigger_type, Trigger):
            raise ExtensionError(f"Class {class_name} of {package_or_path} is not a Trigger subclass")

        self.logger.info("loaded type %s of package %s", class_name, package_or_path)
        return trigger_type

    def on_result(self, result: Result, packages: list[Package]) -> None:
        """
        run trigger with result of application run

        Args:
            result(Result): build result
            packages(list[Package]): list of all available packages
        """
        self.logger.debug("executing triggers on result")
        for trigger in self.triggers:
            with self.__execute_trigger(trigger):
                trigger.on_result(result, packages)

    def on_start(self) -> None:
        """
        run triggers on load
        """
        self.logger.debug("executing triggers on start")
        for trigger in self.triggers:
            with self.__execute_trigger(trigger):
                trigger.on_start()
        # register on_stop call
        atexit.register(self.on_stop)

    def on_stop(self) -> None:
        """
        run triggers before the application exit
        """
        self.logger.debug("executing triggers on stop")
        for trigger in reversed(self.triggers):
            with self.__execute_trigger(trigger):
                trigger.on_stop()
