#
# Copyright (c) 2021-2022 ahriman team.
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

from typing import Type

from ahriman.application.application import Application
from ahriman.application.handlers.handler import Handler
from ahriman.core.configuration import Configuration
from ahriman.models.action import Action


class StatusUpdate(Handler):
    """
    status update handler
    """

    ALLOW_AUTO_ARCHITECTURE_RUN = False

    @classmethod
    def run(cls: Type[Handler], args: argparse.Namespace, architecture: str,
            configuration: Configuration, no_report: bool, unsafe: bool) -> None:
        """
        callback for command line
        :param args: command line args
        :param architecture: repository architecture
        :param configuration: configuration instance
        :param no_report: force disable reporting
        :param unsafe: if set no user check will be performed before path creation
        """
        # we are using reporter here
        client = Application(architecture, configuration, no_report=False, unsafe=unsafe).repository.reporter

        if args.action == Action.Update and args.package:
            # update packages statuses
            for package in args.package:
                client.update(package, args.status)
        elif args.action == Action.Update:
            # update service status
            client.update_self(args.status)
        elif args.action == Action.Remove:
            for package in args.package:
                client.remove(package)
