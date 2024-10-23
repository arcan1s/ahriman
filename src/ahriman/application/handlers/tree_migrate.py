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

from ahriman.application.handlers.handler import Handler, SubParserAction
from ahriman.core.configuration import Configuration
from ahriman.models.repository_id import RepositoryId
from ahriman.models.repository_paths import RepositoryPaths


class TreeMigrate(Handler):
    """
    tree migration handler
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
        current_tree = configuration.repository_paths
        target_tree = RepositoryPaths(current_tree.root, current_tree.repository_id, _force_current_tree=True)

        # create repository tree
        target_tree.tree_create()
        # perform migration
        TreeMigrate.tree_move(current_tree, target_tree)

    @staticmethod
    def _set_service_tree_migrate_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for tree migration subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("service-tree-migrate", help="migrate repository tree",
                                 description="migrate repository tree between versions")
        parser.set_defaults(lock=None, quiet=True, report=False)
        return parser

    @staticmethod
    def tree_move(from_tree: RepositoryPaths, to_tree: RepositoryPaths) -> None:
        """
        move files between trees. Trees must be created in advance

        Args:
            from_tree(RepositoryPaths): old repository tree
            to_tree(RepositoryPaths): new repository tree
        """
        # we don't care about devtools chroot
        for attribute in (
            RepositoryPaths.packages,
            RepositoryPaths.pacman,
            RepositoryPaths.repository,
        ):
            attribute.fget(from_tree).rename(attribute.fget(to_tree))  # type: ignore[attr-defined]

    arguments = [_set_service_tree_migrate_parser]
