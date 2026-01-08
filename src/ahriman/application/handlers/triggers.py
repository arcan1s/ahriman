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
from ahriman.models.repository_id import RepositoryId
from ahriman.models.result import Result


class Triggers(Handler):
    """
    triggers handlers
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
        if args.trigger:
            loader = application.repository.triggers
            loader.triggers = [loader.load_trigger(trigger, repository_id, configuration) for trigger in args.trigger]
        application.on_start()
        application.on_result(Result())

    @staticmethod
    def _set_repo_report_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for report subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("repo-report", aliases=["report"], help="generate report",
                                 description="generate repository report according to current settings",
                                 epilog="Create and/or update repository report as configured.")
        parser.set_defaults(trigger=["ahriman.core.report.ReportTrigger"])
        return parser

    @staticmethod
    def _set_repo_sync_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for repository sync subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("repo-sync", aliases=["sync"], help="sync repository",
                                 description="sync repository files to remote server according to current settings",
                                 epilog="Synchronize the repository to remote services as configured.")
        parser.set_defaults(trigger=["ahriman.core.upload.UploadTrigger"])
        return parser

    @staticmethod
    def _set_repo_triggers_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for repository triggers subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("repo-triggers", help="run triggers",
                                 description="run triggers on empty build result as configured by settings")
        parser.add_argument("trigger", help="instead of running all triggers as set by configuration, just process "
                                            "specified ones in order of mention", nargs="*")
        return parser

    arguments = [
        _set_repo_report_parser,
        _set_repo_sync_parser,
        _set_repo_triggers_parser,
    ]
