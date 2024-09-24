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
import argparse

from ahriman.application.application import Application
from ahriman.application.handlers.handler import Handler
from ahriman.core.configuration import Configuration
from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.package import Package
from ahriman.models.packagers import Packagers
from ahriman.models.repository_id import RepositoryId


class Rebuild(Handler):
    """
    make world handler
    """

    @classmethod
    def run(cls, args: argparse.Namespace, repository_id: RepositoryId, configuration: Configuration, *,
            report: bool) -> None:
        """
        callback for command line

        Args:
            args(argparse.Namespace): command line args
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
            report(bool): force enable or disable reporting
        """
        application = Application(repository_id, configuration, report=report)
        application.on_start()

        packages = Rebuild.extract_packages(application, args.status, from_database=args.from_database)
        packages = application.repository.packages_depend_on(packages, args.depends_on)

        Rebuild.check_status(args.exit_code, packages)
        if args.dry_run:
            application.print_updates(packages, log_fn=print)
            return

        result = application.update(packages, Packagers(args.username), bump_pkgrel=args.increment)
        Rebuild.check_status(args.exit_code, not result.is_empty)

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
                for (package, last_status) in application.reporter.package_get(None)
                if status is None or last_status.status == status
            ]

        return application.repository.packages()
