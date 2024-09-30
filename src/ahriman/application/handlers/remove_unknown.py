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
from ahriman.core.formatters import StringPrinter
from ahriman.models.repository_id import RepositoryId


class RemoveUnknown(Handler):
    """
    remove unknown packages handler
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
        unknown_packages = application.unknown()

        if args.dry_run:
            for package in sorted(unknown_packages):
                StringPrinter(package)(verbose=False)
            return

        application.remove(unknown_packages)

    @staticmethod
    def _set_repo_remove_unknown_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for remove unknown packages subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("repo-remove-unknown", aliases=["remove-unknown"], help="remove unknown packages",
                                 description="remove packages which are missing in AUR and do not have local PKGBUILDs")
        parser.add_argument("--dry-run", help="just perform check for packages without removal", action="store_true")
        return parser

    arguments = [_set_repo_remove_unknown_parser]
