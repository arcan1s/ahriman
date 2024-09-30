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
from ahriman.application.handlers.handler import Handler, SubParserAction
from ahriman.core.configuration import Configuration
from ahriman.core.utils import enum_values, extract_user
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
    def _set_repo_rebuild_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for repository rebuild subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("repo-rebuild", aliases=["rebuild"], help="rebuild repository",
                                 description="force rebuild whole repository")
        parser.add_argument("--depends-on", help="only rebuild packages that depend on specified packages",
                            action="append")
        parser.add_argument("--dry-run", help="just perform check for packages without rebuild process itself",
                            action="store_true")
        parser.add_argument("--from-database",
                            help="read packages from database instead of filesystem. This feature in particular is "
                                 "required in case if you would like to restore repository from another repository "
                                 "instance. Note, however, that in order to restore packages you need to have original "
                                 "ahriman instance run with web service and have run repo-update at least once.",
                            action="store_true")
        parser.add_argument("--increment", help="increment package release (pkgrel) on duplicate",
                            action=argparse.BooleanOptionalAction, default=True)
        parser.add_argument("-e", "--exit-code", help="return non-zero exit status if result is empty",
                            action="store_true")
        parser.add_argument("-s", "--status", help="filter packages by status. Requires --from-database to be set",
                            type=BuildStatusEnum, choices=enum_values(BuildStatusEnum))
        parser.add_argument("-u", "--username", help="build as user", default=extract_user())
        return parser

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

    arguments = [_set_repo_rebuild_parser]
