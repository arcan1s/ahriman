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
import code
import sys

from pathlib import Path

from ahriman.application.handlers.handler import Handler, SubParserAction
from ahriman.core.configuration import Configuration
from ahriman.core.formatters import StringPrinter
from ahriman.models.repository_id import RepositoryId


class Shell(Handler):
    """
    python shell handler
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
        if args.verbose:
            # licensed by https://creativecommons.org/licenses/by-sa/3.0
            path = Path(sys.prefix) / "share" / "ahriman" / "templates" / "shell"
            StringPrinter(path.read_text(encoding="utf8"))(verbose=False)

        local_variables = {
            "architecture": repository_id.architecture,
            "configuration": configuration,
            "repository_id": repository_id,
        }

        if args.code is None:
            code.interact(local=local_variables)
        else:
            code.InteractiveConsole(locals=local_variables).runcode(args.code)

    @staticmethod
    def _set_service_shell_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for shell subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("service-shell", aliases=["shell"], help="invoke python shell",
                                 description="drop into python shell")
        parser.add_argument("code", help="instead of dropping into shell, just execute the specified code", nargs="?")
        parser.add_argument("-v", "--verbose", help=argparse.SUPPRESS, action="store_true")
        parser.set_defaults(lock=None, report=False)
        return parser

    arguments = [_set_service_shell_parser]
