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

from collections.abc import Generator

from ahriman.application.handlers import Handler
from ahriman.core.configuration import Configuration
from ahriman.core.spawn import Spawn
from ahriman.models.repository_id import RepositoryId


class Web(Handler):
    """
    web server handler
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
        # we are using local import for optional dependencies
        from ahriman.web.web import run_server, setup_server

        spawner_args = Web.extract_arguments(args, configuration)
        spawner = Spawn(args.parser(), list(spawner_args))
        spawner.start()

        dummy_args = argparse.Namespace(
            architecture=None,
            configuration=args.configuration,
            repository=None,
            repository_id=None,
        )
        repositories = cls.repositories_extract(dummy_args)
        application = setup_server(configuration, spawner, repositories)
        run_server(application)

        # terminate spawn process at the last
        spawner.stop()
        spawner.join()

    @staticmethod
    def extract_arguments(args: argparse.Namespace, configuration: Configuration) -> Generator[str, None, None]:
        """
        extract list of arguments used for current command, except for command specific ones

        Args:
            args(argparse.Namespace): command line args
            configuration(Configuration): configuration instance

        Returns:
            Generator[str, None, None]: command line arguments which were used for this specific command
        """
        # read configuration path from current settings
        if (configuration_path := configuration.path) is not None:
            yield from ["--configuration", str(configuration_path)]

        # arguments from command line
        if args.force:
            yield "--force"
        if args.log_handler is not None:
            yield from ["--log-handler", args.log_handler.value]
        if args.quiet:
            yield "--quiet"
        if args.unsafe:
            yield "--unsafe"

        # arguments from configuration
        if (wait_timeout := configuration.getint("web", "wait_timeout", fallback=None)) is not None:
            yield from ["--wait-timeout", str(wait_timeout)]
