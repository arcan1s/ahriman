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

from ahriman.application.handlers.handler import SubParserAction
from ahriman.application.handlers.triggers import Triggers


class TriggersSupport(Triggers):
    """
    additional triggers handlers for support commands
    """

    @staticmethod
    def _set_repo_create_keyring_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for create-keyring subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("repo-create-keyring", help="create keyring package",
                                 description="create package which contains list of trusted keys as set by "
                                             "configuration. Note, that this action will only create package, "
                                             "the package itself has to be built manually")
        parser.set_defaults(trigger=["ahriman.core.support.KeyringTrigger"])
        return parser

    @staticmethod
    def _set_repo_create_mirrorlist_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for create-mirrorlist subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("repo-create-mirrorlist", help="create mirrorlist package",
                                 description="create package which contains list of available mirrors as set by "
                                             "configuration. Note, that this action will only create package, "
                                             "the package itself has to be built manually")
        parser.set_defaults(trigger=["ahriman.core.support.MirrorlistTrigger"])
        return parser

    arguments = [
        _set_repo_create_keyring_parser,
        _set_repo_create_mirrorlist_parser,
    ]
