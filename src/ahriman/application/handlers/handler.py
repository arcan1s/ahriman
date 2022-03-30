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
from __future__ import annotations

import argparse
import logging

from multiprocessing import Pool
from typing import List, Type

from ahriman.application.lock import Lock
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import ExitCode, MissingArchitecture, MultipleArchitectures
from ahriman.models.repository_paths import RepositoryPaths


class Handler:
    """
    base handler class for command callbacks
    :cvar ALLOW_AUTO_ARCHITECTURE_RUN: allow to define architecture from existing repositories
    :cvar ALLOW_MULTI_ARCHITECTURE_RUN: allow to run with multiple architectures
    """

    ALLOW_AUTO_ARCHITECTURE_RUN = True
    ALLOW_MULTI_ARCHITECTURE_RUN = True

    @classmethod
    def architectures_extract(cls: Type[Handler], args: argparse.Namespace) -> List[str]:
        """
        get known architectures
        :param args: command line args
        :return: list of architectures for which tree is created
        """
        if not cls.ALLOW_AUTO_ARCHITECTURE_RUN and args.architecture is None:
            # for some parsers (e.g. config) we need to run with specific architecture
            # for those cases architecture must be set explicitly
            raise MissingArchitecture(args.command)
        if args.architecture:  # architecture is specified explicitly
            return sorted(set(args.architecture))

        config = Configuration()
        config.load(args.configuration)
        # wtf???
        root = config.getpath("repository", "root")  # pylint: disable=assignment-from-no-return
        architectures = RepositoryPaths.known_architectures(root)

        if not architectures:  # well we did not find anything
            raise MissingArchitecture(args.command)
        return sorted(architectures)

    @classmethod
    def call(cls: Type[Handler], args: argparse.Namespace, architecture: str) -> bool:
        """
        additional function to wrap all calls for multiprocessing library
        :param args: command line args
        :param architecture: repository architecture
        :return: True on success, False otherwise
        """
        try:
            configuration = Configuration.from_path(args.configuration, architecture, args.quiet)
            with Lock(args, architecture, configuration):
                cls.run(args, architecture, configuration, args.no_report, args.unsafe)
            return True
        except ExitCode:
            return False
        except Exception:
            # we are basically always want to print error to stderr instead of default logger
            logging.getLogger("stderr").exception("process exception")
            return False

    @classmethod
    def execute(cls: Type[Handler], args: argparse.Namespace) -> int:
        """
        execute function for all aru
        :param args: command line args
        :return: 0 on success, 1 otherwise
        """
        architectures = cls.architectures_extract(args)

        # actually we do not have to spawn another process if it is single-process application, do we?
        if len(architectures) > 1:
            if not cls.ALLOW_MULTI_ARCHITECTURE_RUN:
                raise MultipleArchitectures(args.command)

            with Pool(len(architectures)) as pool:
                result = pool.starmap(
                    cls.call, [(args, architecture) for architecture in architectures])
        else:
            result = [cls.call(args, architectures.pop())]

        return 0 if all(result) else 1

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
        raise NotImplementedError
