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

from typing import List, Type

from ahriman.application.application import Application
from ahriman.application.handlers.handler import Handler
from ahriman.core.configuration import Configuration
from ahriman.core.formatters.update_printer import UpdatePrinter
from ahriman.models.package import Package


class Rebuild(Handler):
    """
    make world handler
    """

    @classmethod
    def run(cls: Type[Handler], args: argparse.Namespace, architecture: str,
            configuration: Configuration, no_report: bool, unsafe: bool) -> None:
        """
        callback for command line
        :param args: command line args
        :param architecture: repository architecture
        :param configuration: configuration instance
        :param no_report: force disable reporting
        :param unsafe: if set no user check will be performed before path creation
        """
        depends_on = set(args.depends_on) if args.depends_on else None

        application = Application(architecture, configuration, no_report, unsafe)
        if args.from_database:
            updates = Rebuild.extract_packages(application)
        else:
            updates = application.repository.packages_depends_on(depends_on)

        Rebuild.check_if_empty(args.exit_code, not updates)
        if args.dry_run:
            for package in updates:
                UpdatePrinter(package, package.version).print(verbose=True)
            return

        result = application.update(updates)
        Rebuild.check_if_empty(args.exit_code, result.is_empty)

    @staticmethod
    def extract_packages(application: Application) -> List[Package]:
        """
        extract packages from database file
        :param application: application instance
        :return: list of packages which were stored in database
        """
        return [package for (package, _) in application.database.packages_get()]
