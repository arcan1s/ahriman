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
import argparse

from collections.abc import Callable

from ahriman.application.application import Application
from ahriman.application.handlers.handler import Handler, SubParserAction
from ahriman.core.configuration import Configuration
from ahriman.core.formatters import PackagePrinter, StatusPrinter
from ahriman.core.types import Comparable
from ahriman.core.utils import enum_values
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.package import Package
from ahriman.models.repository_id import RepositoryId


class Status(Handler):
    """
    package status handler
    """

    ALLOW_MULTI_ARCHITECTURE_RUN = False  # conflicting io

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
        # we are using reporter here
        client = Application(repository_id, configuration, report=True).repository.reporter
        if args.ahriman:
            service_status = client.status_get()
            StatusPrinter(service_status.status)(verbose=args.info)
        if args.package:
            packages: list[tuple[Package, BuildStatus]] = sum(
                (client.package_get(base) for base in args.package),
                start=[])
        else:
            packages = client.package_get(None)

        Status.check_status(args.exit_code, packages)

        comparator: Callable[[tuple[Package, BuildStatus]], Comparable] = lambda item: item[0].base
        filter_fn: Callable[[tuple[Package, BuildStatus]], bool] =\
            lambda item: args.status is None or item[1].status == args.status
        for package, package_status in sorted(filter(filter_fn, packages), key=comparator):
            PackagePrinter(package, package_status)(verbose=args.info)

    @staticmethod
    def _set_package_status_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for package status subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("package-status", aliases=["status"], help="get package status",
                                 description="request status of the package",
                                 epilog="This command requests package status from the web interface "
                                        "if it is available.")
        parser.add_argument("package", help="filter status by package base", nargs="*")
        parser.add_argument("--ahriman", help="get service status itself", action="store_true")
        parser.add_argument("-e", "--exit-code", help="return non-zero exit status if result is empty",
                            action="store_true")
        parser.add_argument("--info", help="show additional package information",
                            action=argparse.BooleanOptionalAction, default=False)
        parser.add_argument("-s", "--status", help="filter packages by status",
                            type=BuildStatusEnum, choices=enum_values(BuildStatusEnum))
        parser.set_defaults(lock=None, quiet=True, report=False, unsafe=True)
        return parser

    arguments = [_set_package_status_parser]
