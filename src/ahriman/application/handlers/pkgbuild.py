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

from dataclasses import replace

from ahriman.application.application import Application
from ahriman.application.handlers.handler import Handler, SubParserAction
from ahriman.core.configuration import Configuration
from ahriman.core.formatters import PkgbuildPrinter
from ahriman.models.action import Action
from ahriman.models.repository_id import RepositoryId


class Pkgbuild(Handler):
    """
    package pkgbuild handler
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
        client = application.repository.reporter

        match args.action:
            case Action.List:
                changes = client.package_changes_get(args.package)
                PkgbuildPrinter(changes)(verbose=True, separator="")
                Pkgbuild.check_status(args.exit_code, changes.pkgbuild is not None)
            case Action.Remove:
                changes = client.package_changes_get(args.package)
                client.package_changes_update(args.package, replace(changes, pkgbuild=None))

    @staticmethod
    def _set_package_pkgbuild_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for package pkgbuild subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("package-pkgbuild", help="get package pkgbuild",
                                 description="retrieve package PKGBUILD stored in database",
                                 epilog="This command requests package status from the web interface "
                                        "if it is available.")
        parser.add_argument("package", help="package base")
        parser.add_argument("-e", "--exit-code", help="return non-zero exit status if result is empty",
                            action="store_true")
        parser.set_defaults(action=Action.List, lock=None, quiet=True, report=False, unsafe=True)
        return parser

    @staticmethod
    def _set_package_pkgbuild_remove_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for package pkgbuild remove subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("package-pkgbuild-remove", help="remove package pkgbuild",
                                 description="remove the package PKGBUILD stored remotely")
        parser.add_argument("package", help="package base")
        parser.set_defaults(action=Action.Remove, exit_code=False, lock=None, quiet=True, report=False, unsafe=True)
        return parser

    arguments = [_set_package_pkgbuild_parser, _set_package_pkgbuild_remove_parser]
