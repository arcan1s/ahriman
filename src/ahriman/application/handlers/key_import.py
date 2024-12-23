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
from ahriman.models.repository_id import RepositoryId


class KeyImport(Handler):
    """
    key import packages handler
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
        application = Application(repository_id, configuration, report=report)
        application.repository.sign.key_import(args.key_server, args.key)

    @staticmethod
    def _set_service_key_import_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for key import subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("service-key-import", aliases=["key-import"], help="import PGP key",
                                 description="import PGP key from public sources to the repository user",
                                 epilog="By default ahriman runs build process with package sources validation "
                                        "(in case if signature and keys are available in PKGBUILD). This process will "
                                        "fail in case if key is not known for build user. This subcommand can be used "
                                        "in order to import the PGP key to user keychain.")
        parser.add_argument("--key-server", help="key server for key import", default="keyserver.ubuntu.com")
        parser.add_argument("key", help="PGP key to import from public server")
        parser.set_defaults(architecture="", lock=None, report=False, repository="")
        return parser

    arguments = [_set_service_key_import_parser]
