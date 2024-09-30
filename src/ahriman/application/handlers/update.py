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

from collections.abc import Callable

from ahriman.application.application import Application
from ahriman.application.handlers.handler import Handler, SubParserAction
from ahriman.core.configuration import Configuration
from ahriman.core.utils import extract_user
from ahriman.models.packagers import Packagers
from ahriman.models.repository_id import RepositoryId


class Update(Handler):
    """
    package update handler
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
        application.on_start()

        packages = application.updates(args.package, aur=args.aur, local=args.local, manual=args.manual, vcs=args.vcs,
                                       check_files=args.check_files)
        if args.changes:  # generate changes if requested
            application.changes(packages)

        if args.dry_run:  # exit from application if no build requested
            Update.check_status(args.exit_code, packages)  # status code check
            return

        packages = application.with_dependencies(packages, process_dependencies=args.dependencies)
        packagers = Packagers(args.username, {package.base: package.packager for package in packages})

        application.print_updates(packages, log_fn=application.logger.info)
        result = application.update(packages, packagers, bump_pkgrel=args.increment)
        Update.check_status(args.exit_code, not result.is_empty)

    @staticmethod
    def _set_repo_check_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for repository check subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("repo-check", aliases=["check"], help="check for updates",
                                 description="check for packages updates. Same as repo-update --dry-run --no-manual")
        parser.add_argument("package", help="filter check by package base", nargs="*")
        parser.add_argument("--changes", help="calculate changes from the latest known commit if available",
                            action=argparse.BooleanOptionalAction, default=True)
        parser.add_argument("--check-files", help="enable or disable checking of broken dependencies "
                                                  "(e.g. dynamically linked libraries or modules directories)",
                            action=argparse.BooleanOptionalAction, default=True)
        parser.add_argument("-e", "--exit-code", help="return non-zero exit status if result is empty",
                            action="store_true")
        parser.add_argument("--vcs", help="fetch actual version of VCS packages",
                            action=argparse.BooleanOptionalAction, default=True)
        parser.add_argument("-y", "--refresh", help="download fresh package databases from the mirror before actions, "
                                                    "-yy to force refresh even if up to date",
                            action="count", default=False)
        parser.set_defaults(aur=True, dependencies=False, dry_run=True, increment=False, local=True, manual=False,
                            username=None)
        return parser

    @staticmethod
    def _set_repo_update_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for repository update subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("repo-update", aliases=["update"], help="update packages",
                                 description="check for packages updates and run build process if requested")
        parser.add_argument("package", help="filter check by package base", nargs="*")
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
        parser.add_argument("-e", "--exit-code", help="return non-zero exit status if result is empty",
                            action="store_true")
        parser.add_argument("--increment", help="increment package release (pkgrel) on duplicate",
                            action=argparse.BooleanOptionalAction, default=True)
        parser.add_argument("--local", help="enable or disable checking of local packages for updates",
                            action=argparse.BooleanOptionalAction, default=True)
        parser.add_argument("--manual", help="include or exclude manual updates",
                            action=argparse.BooleanOptionalAction, default=True)
        parser.add_argument("-u", "--username", help="build as user", default=extract_user())
        parser.add_argument("--vcs", help="fetch actual version of VCS packages",
                            action=argparse.BooleanOptionalAction, default=True)
        parser.add_argument("-y", "--refresh", help="download fresh package databases from the mirror before actions, "
                                                    "-yy to force refresh even if up to date",
                            action="count", default=False)
        return parser

    @staticmethod
    def log_fn(application: Application, dry_run: bool) -> Callable[[str], None]:
        """
        package updates log function

        Args:
            application(Application): application instance
            dry_run(bool): do not perform update itself

        Returns:
            Callable[[str], None]: in case if dry_run is set it will return print, logger otherwise
        """
        def inner(line: str) -> None:
            return print(line) if dry_run else application.logger.info(line)  # pylint: disable=bad-builtin
        return inner

    arguments = [
        _set_repo_check_parser,
        _set_repo_update_parser,
    ]
