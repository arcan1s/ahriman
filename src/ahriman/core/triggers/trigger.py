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
from typing import Iterable

from ahriman.core.configuration import Configuration
from ahriman.core.lazy_logging import LazyLogging
from ahriman.models.package import Package
from ahriman.models.result import Result


class Trigger(LazyLogging):
    """
    trigger base class

    Attributes:
        architecture(str): repository architecture
        configuration(Configuration): configuration instance

    Examples:
        This class must be used in order to create own extension. Basically idea is the following::

            >>> class CustomTrigger(Trigger):
            >>>     def run(self, result: Result, packages: Iterable[Package]) -> None:
            >>>         perform_some_action()

        Having this class you can pass it to ``configuration`` and it will be run on action::

            >>> from ahriman.core.triggers import TriggerLoader
            >>>
            >>> configuration = Configuration()
            >>> configuration.set_option("build", "triggers", "my.awesome.package.CustomTrigger")
            >>>
            >>> loader = TriggerLoader("x86_64", configuration)
            >>> loader.process(Result(), [])
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

    def run(self, result: Result, packages: Iterable[Package]) -> None:
        """
        run trigger

        Args:
            result(Result): build result
            packages(Iterable[Package]): list of all available packages

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError
