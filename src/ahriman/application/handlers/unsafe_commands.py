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

from ahriman.application.handlers import Handler
from ahriman.core.configuration import Configuration
from ahriman.core.formatters import StringPrinter


class UnsafeCommands(Handler):
    """
    unsafe command help parser
    """

    ALLOW_AUTO_ARCHITECTURE_RUN = False  # it should be called only as "no-architecture"

    @classmethod
    def run(cls, args: argparse.Namespace, architecture: str, configuration: Configuration, *,
            report: bool, unsafe: bool) -> None:
        """
        callback for command line

        Args:
            args(argparse.Namespace): command line args
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
            report(bool): force enable or disable reporting
            unsafe(bool): if set no user check will be performed before path creation
        """
        parser = args.parser()
        unsafe_commands = UnsafeCommands.get_unsafe_commands(parser)
        if args.command:
            UnsafeCommands.check_unsafe(args.command, unsafe_commands, parser)
        else:
            for command in unsafe_commands:
                StringPrinter(command).print(verbose=True)

    @staticmethod
    def check_unsafe(command: list[str], unsafe_commands: list[str], parser: argparse.ArgumentParser) -> None:
        """
        check if command is unsafe

        Args:
            command(str): command to check
            unsafe_commands(list[str]): list of unsafe commands
            parser(argparse.ArgumentParser): generated argument parser
        """
        args = parser.parse_args(command)
        UnsafeCommands.check_if_empty(True, args.command in unsafe_commands)

    @staticmethod
    def get_unsafe_commands(parser: argparse.ArgumentParser) -> list[str]:
        """
        extract unsafe commands from argument parser

        Args:
            parser(argparse.ArgumentParser): generated argument parser

        Returns:
            list[str]: list of commands with default unsafe flag
        """
        # should never fail
        # pylint: disable=protected-access
        subparser = next((action for action in parser._actions if isinstance(action, argparse._SubParsersAction)), None)
        actions = subparser.choices if subparser is not None else {}
        return sorted(action_name for action_name, action in actions.items() if action.get_default("unsafe"))
