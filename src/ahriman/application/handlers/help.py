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

from ahriman.application.handlers.handler import Handler, SubParserAction
from ahriman.core.configuration import Configuration
from ahriman.models.repository_id import RepositoryId


class Help(Handler):
    """
    help handler
    """

    ALLOW_MULTI_ARCHITECTURE_RUN = False  # system-wide action

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
        parser: argparse.ArgumentParser = args.parser()
        if args.subcommand is None:
            parser.parse_args(["--help"])
        else:
            parser.parse_args([args.subcommand, "--help"])

    @staticmethod
    def _set_help_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for listing help subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("help", help="show help message",
                                 description="show help message for application or command and exit")
        parser.add_argument("subcommand", help="show help message for specific command", nargs="?")
        parser.set_defaults(architecture="", lock=None, quiet=True, report=False, repository="", unsafe=True)
        return parser

    arguments = [_set_help_parser]
