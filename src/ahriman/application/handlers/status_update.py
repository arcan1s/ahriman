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
from ahriman.core.utils import enum_values
from ahriman.models.action import Action
from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.repository_id import RepositoryId


class StatusUpdate(Handler):
    """
    status update handler
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
            case Action.Update if args.package:
                # update packages statuses
                for package in args.package:
                    client.package_status_update(package, args.status)
            case Action.Update:
                # update service status
                client.status_update(args.status)
            case Action.Remove:
                for package in args.package:
                    client.package_remove(package)

    @staticmethod
    def _set_package_status_remove_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for package status remove subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("package-status-remove", help="remove package status",
                                 description="remove the package from the status page",
                                 epilog="Please note that this subcommand does not remove the package itself, it just "
                                        "clears the status page.")
        parser.add_argument("package", help="remove specified packages from status page", nargs="+")
        parser.set_defaults(action=Action.Remove, lock=None, quiet=True, report=False, unsafe=True)
        return parser

    @staticmethod
    def _set_package_status_update_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for package status update subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("package-status-update", aliases=["status-update"], help="update package status",
                                 description="update package status on the status page")
        parser.add_argument("package", help="set status for specified packages. "
                                            "If no packages supplied, service status will be updated",
                            nargs="*")
        parser.add_argument("-s", "--status", help="new package build status",
                            type=BuildStatusEnum, choices=enum_values(BuildStatusEnum), default=BuildStatusEnum.Success)
        parser.set_defaults(action=Action.Update, lock=None, quiet=True, report=False, unsafe=True)
        return parser

    @staticmethod
    def _set_repo_status_update_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for repository status update subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("repo-status-update", help="update repository status",
                                 description="update repository status on the status page")
        parser.add_argument("-s", "--status", help="new status",
                            type=BuildStatusEnum, choices=enum_values(BuildStatusEnum), default=BuildStatusEnum.Success)
        parser.set_defaults(action=Action.Update, lock=None, package=[], quiet=True, report=False, unsafe=True)
        return parser

    arguments = [
        _set_package_status_remove_parser,
        _set_package_status_update_parser,
        _set_repo_status_update_parser,
    ]
