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
from ahriman.application.handlers.handler import Handler
from ahriman.core.configuration import Configuration
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
        if args.dry_run:  # some check specific actions
            if args.changes:  # generate changes if requested
                application.changes(packages)

            Update.check_if_empty(args.exit_code, not packages)  # status code check
            return

        packages = application.with_dependencies(packages, process_dependencies=args.dependencies)
        packagers = Packagers(args.username, {package.base: package.packager for package in packages})

        application.print_updates(packages, log_fn=application.logger.info)
        result = application.update(packages, packagers, bump_pkgrel=args.increment)
        Update.check_if_empty(args.exit_code, result.is_empty)

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
            return print(line) if dry_run else application.logger.info(line)
        return inner
