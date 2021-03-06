#
# Copyright (c) 2021 ahriman team.
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

from typing import Callable, Type

from ahriman.application.application import Application
from ahriman.application.handlers.handler import Handler
from ahriman.core.configuration import Configuration


class Update(Handler):
    """
    package update handler
    """

    @classmethod
    def run(cls: Type[Handler], args: argparse.Namespace, architecture: str, configuration: Configuration) -> None:
        """
        callback for command line
        :param args: command line args
        :param architecture: repository architecture
        :param configuration: configuration instance
        """
        application = Application(architecture, configuration)
        packages = application.get_updates(args.package, args.no_aur, args.no_manual, args.no_vcs,
                                           Update.log_fn(application, args.dry_run))
        if args.dry_run:
            return

        application.update(packages)

    @staticmethod
    def log_fn(application: Application, dry_run: bool) -> Callable[[str], None]:
        """
        package updates log function
        :param application: application instance
        :param dry_run: do not perform update itself
        :return: in case if dry_run is set it will return print, logger otherwise
        """
        def inner(line: str) -> None:
            return print(line) if dry_run else application.logger.info(line)
        return inner
