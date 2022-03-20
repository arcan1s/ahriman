#
# Copyright (c) 2021 ahriman team.
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

from ahriman.application.handlers.handler import Handler
from ahriman.core.configuration import Configuration
from ahriman.core.formatters.string_printer import StringPrinter


class UnsafeCommands(Handler):
    """
    unsafe command help parser
    """

    ALLOW_AUTO_ARCHITECTURE_RUN = False  # it should be called only as "no-architecture"

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
        unsafe_commands = UnsafeCommands.get_unsafe_commands(args.parser())
        for command in unsafe_commands:
            StringPrinter(command).print(verbose=True)

    @staticmethod
    def get_unsafe_commands(parser: argparse.ArgumentParser) -> List[str]:
        """
        extract unsafe commands from argument parser
        :param parser: generated argument parser
        :return: list of commands with default unsafe flag
        """
        # pylint: disable=protected-access
        subparser = next(action for action in parser._actions if isinstance(action, argparse._SubParsersAction))
        return [action_name for action_name, action in subparser.choices.items() if action.get_default("unsafe")]