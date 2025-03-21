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
import tarfile

from pathlib import Path

from ahriman.application.handlers.handler import Handler, SubParserAction
from ahriman.core.configuration import Configuration
from ahriman.models.repository_id import RepositoryId


class Restore(Handler):
    """
    restore packages handler
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
        with tarfile.open(args.path) as archive:
            archive.extractall(path=args.output)  # nosec

    @staticmethod
    def _set_repo_restore_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for repository restore subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("repo-restore", help="restore repository data",
                                 description="restore settings and database")
        parser.add_argument("path", help="path of the input archive", type=Path)
        parser.add_argument("-o", "--output", help="root path of the extracted files", type=Path, default=Path("/"))
        parser.set_defaults(architecture="", lock=None, report=False, repository="", unsafe=True)
        return parser

    arguments = [_set_repo_restore_parser]
