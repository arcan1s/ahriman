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

from ahriman.application.application import Application
from ahriman.application.handlers.handler import Handler, SubParserAction
from ahriman.core.configuration import Configuration
from ahriman.core.formatters import StringPrinter, TreePrinter
from ahriman.core.tree import Tree
from ahriman.models.repository_id import RepositoryId


class Structure(Handler):
    """
    dump repository structure handler
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
        application = Application(repository_id, configuration, report=report)
        partitions = Tree.partition(application.repository.packages(), count=args.partitions)

        for partition_id, partition in enumerate(partitions):
            StringPrinter(f"partition #{partition_id}")(verbose=False)

            tree = Tree.resolve(partition)
            for num, level in enumerate(tree):
                TreePrinter(num, level)(verbose=True, separator=" ")

            # empty line
            StringPrinter("")(verbose=False)

    @staticmethod
    def _set_repo_tree_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for repository tree subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("repo-tree", help="dump repository tree",
                                 description="dump repository tree based on packages dependencies")
        parser.add_argument("-p", "--partitions", help="also divide packages by independent partitions",
                            type=int, default=1)
        parser.set_defaults(lock=None, quiet=True, report=False, unsafe=True)
        return parser

    arguments = [_set_repo_tree_parser]
