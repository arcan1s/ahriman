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
import argparse

from ahriman.application.application import Application
from ahriman.application.handlers.handler import Handler, SubParserAction
from ahriman.core.configuration import Configuration
from ahriman.core.formatters import PackagePrinter
from ahriman.models.action import Action
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.repository_id import RepositoryId


class Archives(Handler):
    """
    package archives handler
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
        application = Application(repository_id, configuration, report=True)

        match args.action:
            case Action.List:
                archives = application.repository.package_archives(args.package)
                for package in archives:
                    PackagePrinter(package, BuildStatus(BuildStatusEnum.Success))(verbose=args.info)

                Archives.check_status(args.exit_code, bool(archives))

    @staticmethod
    def _set_package_archives_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for package archives subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("package-archives", help="list package archive versions",
                                 description="list available archive versions for the package")
        parser.add_argument("package", help="package base")
        parser.add_argument("-e", "--exit-code", help="return non-zero exit status if result is empty",
                            action="store_true")
        parser.add_argument("--info", help="show additional package information",
                            action=argparse.BooleanOptionalAction, default=False)
        parser.set_defaults(action=Action.List, lock=None, quiet=True, report=False, unsafe=True)
        return parser

    arguments = [_set_package_archives_parser]
