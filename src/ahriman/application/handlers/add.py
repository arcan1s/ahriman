#
# Copyright (c) 2021-2023 ahriman team.
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
from ahriman.application.handlers import Handler
from ahriman.core.configuration import Configuration


class Add(Handler):
    """
    add packages handler
    """

    @classmethod
    def run(cls, args: argparse.Namespace, architecture: str, configuration: Configuration, *,
            report: bool, unsafe: bool) -> None:
        """
        callback for command line

        Args:
            args(argparse.Namespace): command line args
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
            report(bool): force enable or disable reporting
            unsafe(bool): if set no user check will be performed before path creation
        """
        application = Application(architecture, configuration,
                                  report=report, unsafe=unsafe, refresh_pacman_database=args.refresh)
        application.on_start()
        application.add(args.package, args.source)
        if not args.now:
            return

        packages = application.updates(args.package, aur=False, local=False, manual=True, vcs=False,
                                       log_fn=application.logger.info)
        packages = application.with_dependencies(packages, process_dependencies=args.dependencies)
        result = application.update(packages)
        Add.check_if_empty(args.exit_code, result.is_empty)
