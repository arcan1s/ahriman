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
from ahriman.models.action import Action


class StatusUpdate(Handler):
    """
    status update handler
    """

    ALLOW_AUTO_ARCHITECTURE_RUN = False

    @classmethod
    def run(cls, args: argparse.Namespace, architecture: str, configuration: Configuration, *, report: bool) -> None:
        """
        callback for command line

        Args:
            args(argparse.Namespace): command line args
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
            report(bool): force enable or disable reporting
        """
        # we are using reporter here
        client = Application(architecture, configuration, report=True).repository.reporter

        if args.action == Action.Update and args.package:
            # update packages statuses
            for package in args.package:
                client.package_update(package, args.status)
        elif args.action == Action.Update:
            # update service status
            client.status_update(args.status)
        elif args.action == Action.Remove:
            for package in args.package:
                client.package_remove(package)
