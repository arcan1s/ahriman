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
import argparse

from typing import Iterable, Tuple, Type

from ahriman.application.application import Application
from ahriman.application.handlers.handler import Handler
from ahriman.core.configuration import Configuration
from ahriman.models.build_status import BuildStatus
from ahriman.models.package import Package


class Status(Handler):
    """
    package status handler
    """

    @classmethod
    def run(cls: Type[Handler], args: argparse.Namespace, architecture: str, configuration: Configuration) -> None:
        """
        callback for command line
        :param args: command line args
        :param architecture: repository architecture
        :param configuration: configuration instance
        """
        application = Application(architecture, configuration)
        if args.ahriman:
            ahriman = application.repository.reporter.get_self()
            print(ahriman.pretty_print())
            print()
        if args.package:
            packages: Iterable[Tuple[Package, BuildStatus]] = sum(
                [application.repository.reporter.get(base) for base in args.package],
                start=[])
        else:
            packages = application.repository.reporter.get(None)
        for package, package_status in sorted(packages, key=lambda item: item[0].base):
            print(package.pretty_print())
            print(f"\t{package.version}")
            print(f"\t{package_status.pretty_print()}")
