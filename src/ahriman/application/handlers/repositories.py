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
from ahriman.core.formatters import RepositoryPrinter
from ahriman.models.repository_id import RepositoryId


class Repositories(Handler):
    """
    repositories listing handler
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
        dummy_args = argparse.Namespace(
            architecture=None,
            configuration=args.configuration,
            repository=None,
            repository_id=None,
        )
        for repository in cls.repositories_extract(dummy_args):
            RepositoryPrinter(repository)(verbose=not args.id_only)

    @staticmethod
    def _set_service_repositories(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for repositories listing

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("service-repositories", help="show repositories",
                                 description="list all available repositories")
        parser.add_argument("--id-only", help="show machine readable identifier instead",
                            action=argparse.BooleanOptionalAction, default=False)
        parser.set_defaults(architecture="", lock=None, report=False, repository="", unsafe=True)
        return parser

    arguments = [_set_service_repositories]
