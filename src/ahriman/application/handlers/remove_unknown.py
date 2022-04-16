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
import argparse

from typing import Type

from ahriman.application.application import Application
from ahriman.application.handlers.handler import Handler
from ahriman.core.configuration import Configuration
from ahriman.core.formatters.string_printer import StringPrinter


class RemoveUnknown(Handler):
    """
    remove unknown packages handler
    """

    @classmethod
    def run(cls: Type[Handler], args: argparse.Namespace, architecture: str,
            configuration: Configuration, no_report: bool, unsafe: bool) -> None:
        """
        callback for command line

        Args:
          args(argparse.Namespace): command line args
          architecture(str): repository architecture
          configuration(Configuration): configuration instance
          no_report(bool): force disable reporting
          unsafe(bool): if set no user check will be performed before path creation
        """
        application = Application(architecture, configuration, no_report, unsafe)
        unknown_packages = application.unknown()

        if args.dry_run:
            for package in sorted(unknown_packages):
                StringPrinter(package).print(args.info)
            return

        application.remove(unknown_packages)
