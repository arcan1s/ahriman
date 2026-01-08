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


class Clean(Handler):
    """
    clean caches handler
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
        application.clean(cache=args.cache, chroot=args.chroot, manual=args.manual, packages=args.packages,
                          pacman=args.pacman)

    @staticmethod
    def _set_service_clean_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for repository clean subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("service-clean", aliases=["clean", "repo-clean"], help="clean local caches",
                                 description="remove local caches",
                                 epilog="The subcommand clears every temporary directories (builds, caches etc). "
                                        "Normally you should not run this command manually. Also in case if "
                                        "you are going to clear the chroot directories you will need root privileges.")
        parser.add_argument("--cache", help="clear directory with package caches",
                            action=argparse.BooleanOptionalAction, default=False)
        parser.add_argument("--chroot", help="clear build chroot", action=argparse.BooleanOptionalAction, default=False)
        parser.add_argument("--manual", help="clear manually added packages queue",
                            action=argparse.BooleanOptionalAction, default=False)
        parser.add_argument("--packages", help="clear directory with built packages",
                            action=argparse.BooleanOptionalAction, default=False)
        parser.add_argument("--pacman", help="clear directory with pacman local database cache",
                            action=argparse.BooleanOptionalAction, default=False)
        parser.set_defaults(lock=None, quiet=True, unsafe=True)
        return parser

    arguments = [_set_service_clean_parser]
