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
import shlex

from ahriman.application.handlers.handler import Handler, SubParserAction
from ahriman.core.configuration import Configuration
from ahriman.models.repository_id import RepositoryId


class Run(Handler):
    """
    multicommand handler
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
        parser = args.parser()
        for command in args.command:
            status = Run.run_command(shlex.split(command), parser)
            Run.check_status(True, status)

    @staticmethod
    def _set_service_run(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for multicommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("service-run", aliases=["run"], help="run multiple commands",
                                 description="run multiple commands on success run of the previous command",
                                 epilog="Commands must be quoted by using usual bash rules. Processes will be spawned "
                                        "under the same user as this command.")
        parser.add_argument("command", help="command to be run (quoted) without ``ahriman``", nargs="+")
        parser.set_defaults(architecture="", lock=None, report=False, repository="", unsafe=True)
        return parser

    @staticmethod
    def run_command(command: list[str], parser: argparse.ArgumentParser) -> bool:
        """
        run command specified by the argument

        Args:
            command(list[str]): command to run
            parser(argparse.ArgumentParser): generated argument parser

        Returns:
            bool: status of the command
        """
        args = parser.parse_args(command)
        handler: Handler = args.handler
        return handler.execute(args) == 0

    arguments = [_set_service_run]
