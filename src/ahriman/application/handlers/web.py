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

from typing import Type

from ahriman.application.handlers.handler import Handler
from ahriman.core.configuration import Configuration
from ahriman.core.spawn import Spawn


class Web(Handler):
    """
    web server handler
    """

    ALLOW_AUTO_ARCHITECTURE_RUN = False
    ALLOW_MULTI_ARCHITECTURE_RUN = False  # required to be able to spawn external processes

    @classmethod
    def run(cls: Type[Handler], args: argparse.Namespace, architecture: str,
            configuration: Configuration, no_report: bool) -> None:
        """
        callback for command line
        :param args: command line args
        :param architecture: repository architecture
        :param configuration: configuration instance
        :param no_report: force disable reporting
        """
        # we are using local import for optional dependencies
        from ahriman.web.web import run_server, setup_service

        spawner = Spawn(args.parser(), architecture, configuration)
        spawner.start()

        application = setup_service(architecture, configuration, spawner)
        run_server(application)
