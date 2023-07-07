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
import argparse

from ahriman.application.application import Application
from ahriman.application.handlers import Handler
from ahriman.core.configuration import Configuration
from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.package import Package


class Rebuild(Handler):
    """
    make world handler
    """

    @classmethod
    def run(cls, args: argparse.Namespace, architecture: str, configuration: Configuration, *, report: bool) -> None:
        """
        callback for command line

        Args:
            args(argparse.Namespace): command line args
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
            report(bool): force enable or disable reporting
        """
        application = Application(architecture, configuration, report=report)
        application.on_start()

        packages = Rebuild.extract_packages(application, args.status, from_database=args.from_database)
        updates = application.repository.packages_depend_on(packages, args.depends_on or None)

        Rebuild.check_if_empty(args.exit_code, not updates)
        if args.dry_run:
            application.print_updates(updates, log_fn=print)
            return

        result = application.update(updates, args.username)
        Rebuild.check_if_empty(args.exit_code, result.is_empty)

    @staticmethod
    def extract_packages(application: Application, status: BuildStatusEnum | None, *,
                         from_database: bool) -> list[Package]:
        """
        extract packages from database file

        Args:
            application(Application): application instance
            status(BuildStatusEnum | None): optional filter by package status
            from_database(bool): extract packages from database instead of repository filesystem

        Returns:
            list[Package]: list of packages which were stored in database
        """
        if from_database:
            return [
                package
                for (package, last_status) in application.database.packages_get()
                if status is None or last_status.status == status
            ]

        return application.repository.packages()
