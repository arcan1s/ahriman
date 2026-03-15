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
from ahriman.models.action import Action
from ahriman.models.repository_id import RepositoryId


class Hold(Handler):
    """
    package hold handler
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
        client = Application(repository_id, configuration, report=True).reporter

        match args.action:
            case Action.Remove:
                for package in args.package:
                    client.package_hold_update(package, enabled=False)
            case Action.Update:
                for package in args.package:
                    client.package_hold_update(package, enabled=True)

    @staticmethod
    def _set_package_hold_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for hold package subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("package-hold", help="hold package",
                                 description="hold package from automatic updates")
        parser.add_argument("package", help="package base", nargs="+")
        parser.set_defaults(action=Action.Update, lock=None, quiet=True, report=False, unsafe=True)
        return parser

    @staticmethod
    def _set_package_unhold_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for unhold package subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("package-unhold", help="unhold package",
                                 description="remove package hold, allowing automatic updates")
        parser.add_argument("package", help="package base", nargs="+")
        parser.set_defaults(action=Action.Remove, lock=None, quiet=True, report=False, unsafe=True)
        return parser

    arguments = [
        _set_package_hold_parser,
        _set_package_unhold_parser,
    ]
