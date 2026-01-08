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

from pathlib import Path

from ahriman.application.application import Application
from ahriman.application.application.updates_iterator import FixedUpdatesIterator, UpdatesIterator
from ahriman.application.handlers.handler import Handler, SubParserAction
from ahriman.application.handlers.update import Update
from ahriman.core.configuration import Configuration
from ahriman.core.utils import extract_user
from ahriman.models.repository_id import RepositoryId


class Daemon(Handler):
    """
    daemon packages handler
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
        application = Application(repository_id, configuration, report=report, refresh_pacman_database=args.refresh)
        if args.partitions:
            iterator = UpdatesIterator(application, args.interval)
        else:
            iterator = FixedUpdatesIterator(application, args.interval)

        for packages in iterator:
            if packages is None:
                continue  # nothing to check case

            args.package = packages
            Update.run(args, repository_id, configuration, report=report)

    @staticmethod
    def _set_repo_daemon_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for daemon subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("repo-daemon", aliases=["daemon"], help="run application as daemon",
                                 description="start process which periodically will run update process")
        parser.add_argument("-i", "--interval", help="interval between runs in seconds", type=int, default=60 * 60 * 12)
        parser.add_argument("--aur", help="enable or disable checking for AUR updates",
                            action=argparse.BooleanOptionalAction, default=True)
        parser.add_argument("--changes", help="calculate changes from the latest known commit if available. "
                                              "Only applicable in dry run mode",
                            action=argparse.BooleanOptionalAction, default=True)
        parser.add_argument("--check-files", help="enable or disable checking of broken dependencies "
                                                  "(e.g. dynamically linked libraries or modules directories)",
                            action=argparse.BooleanOptionalAction, default=True)
        parser.add_argument("--dependencies", help="process missing package dependencies",
                            action=argparse.BooleanOptionalAction, default=True)
        parser.add_argument("--dry-run", help="just perform check for updates, same as check command",
                            action="store_true")
        parser.add_argument("--increment", help="increment package release (pkgrel) on duplicate",
                            action=argparse.BooleanOptionalAction, default=True)
        parser.add_argument("--local", help="enable or disable checking of local packages for updates",
                            action=argparse.BooleanOptionalAction, default=True)
        parser.add_argument("--manual", help="include or exclude manual updates",
                            action=argparse.BooleanOptionalAction, default=True)
        parser.add_argument("--partitions", help="instead of updating whole repository, split updates into chunks",
                            action=argparse.BooleanOptionalAction, default=True)
        parser.add_argument("-u", "--username", help="build as user", default=extract_user())
        parser.add_argument("--vcs", help="fetch actual version of VCS packages",
                            action=argparse.BooleanOptionalAction, default=True)
        parser.add_argument("-y", "--refresh", help="download fresh package databases from the mirror before actions, "
                                                    "-yy to force refresh even if up to date",
                            action="count", default=False)
        parser.set_defaults(exit_code=False, lock=Path("ahriman-daemon.pid"), package=[])
        return parser

    arguments = [_set_repo_daemon_parser]
