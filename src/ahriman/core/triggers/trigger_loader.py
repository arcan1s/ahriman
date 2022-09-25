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
import contextlib
import importlib
import os
import weakref

from pathlib import Path
from types import ModuleType
from typing import Generator, Iterable

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import InvalidExtension
from ahriman.core.lazy_logging import LazyLogging
from ahriman.core.triggers import Trigger
from ahriman.models.package import Package
from ahriman.models.result import Result


class TriggerLoader(LazyLogging):
    """
    trigger loader class

    Attributes:
        architecture(str): repository architecture
        configuration(Configuration): configuration instance
        triggers(List[Trigger]): list of loaded triggers according to the configuration

    Examples:
        This class more likely must not be used directly, but the usual workflow is the following::

            >>> configuration = Configuration()  # create configuration
            >>> configuration.set_option("build", "triggers", "ahriman.core.report.ReportTrigger")  # set class for load

        Having such configuration you can create instance of the loader::

            >>> loader = TriggerLoader("x86_64", configuration)
            >>> print(loader.triggers)

        After that you are free to run triggers::

            >>> loader.on_result(Result(), [])
    """

    def __init__(self, architecture: str, configuration: Configuration) -> None:
        """
        default constructor

        Args:
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
        """
        self.architecture = architecture
        self.configuration = configuration

        self.triggers = [
            self.load_trigger(trigger)
            for trigger in configuration.getlist("build", "triggers")
        ]

        self.on_start()
        self._finalizer = weakref.finalize(self, self.on_stop)

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
        # Thus, this method should never throw ``FileNotFoundError`` exception
        loader = importlib.machinery.SourceFileLoader(implementation, module_path)
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
            InvalidExtension: in case if module cannot be loaded from specified package
        """
        self.logger.info("load module from package %s", package)
        try:
            return importlib.import_module(package)
        except ModuleNotFoundError:
            raise InvalidExtension(f"Module {package} not found")

    def load_trigger(self, module_path: str) -> Trigger:
        """
        load trigger by module path

        Args:
            module_path(str): module import path to load

        Returns:
            Trigger: loaded trigger based on settings

        Raises:
            InvalidExtension: in case if module cannot be loaded from the specified module path or is not a trigger
        """
        *package_path_parts, class_name = module_path.split(".")
        package_or_path = ".".join(package_path_parts)

        # it works for both missing permission and file does not exist
        path_like = Path(package_or_path)
        if os.access(path_like, os.R_OK) and path_like.is_file():
            module = self._load_module_from_file(package_or_path, class_name)
        else:
            module = self._load_module_from_package(package_or_path)

        trigger_type = getattr(module, class_name, None)
        if not isinstance(trigger_type, type):
            raise InvalidExtension(f"{class_name} of {package_or_path} is not a type")
        self.logger.info("loaded type %s of package %s", class_name, package_or_path)

        try:
            trigger = trigger_type(self.architecture, self.configuration)
        except Exception:
            raise InvalidExtension(f"Could not load instance of trigger from {class_name} of {package_or_path}")
        if not isinstance(trigger, Trigger):
            raise InvalidExtension(f"Class {class_name} of {package_or_path} is not a Trigger")

        return trigger

    def on_result(self, result: Result, packages: Iterable[Package]) -> None:
        """
        run trigger with result of application run

        Args:
            result(Result): build result
            packages(Iterable[Package]): list of all available packages
        """
        for trigger in self.triggers:
            with self.__execute_trigger(trigger):
                trigger.on_result(result, packages)

    def on_start(self) -> None:
        """
        run triggers on load
        """
        for trigger in self.triggers:
            with self.__execute_trigger(trigger):
                trigger.on_start()

    def on_stop(self) -> None:
        """
        run triggers before the application exit
        """
        for trigger in self.triggers:
            with self.__execute_trigger(trigger):
                trigger.on_stop()
