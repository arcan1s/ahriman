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
from __future__ import annotations

import argparse
import logging

from multiprocessing import Pool
from typing import List, Type

from ahriman.application.lock import Lock
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import MissingArchitecture
from ahriman.models.repository_paths import RepositoryPaths


class Handler:
    """
    base handler class for command callbacks
    """

    @classmethod
    def _call(cls: Type[Handler], args: argparse.Namespace, architecture: str) -> bool:
        """
        additional function to wrap all calls for multiprocessing library
        :param args: command line args
        :param architecture: repository architecture
        :return: True on success, False otherwise
        """
        try:
            configuration = Configuration.from_path(args.configuration, architecture, not args.no_log)
            with Lock(args, architecture, configuration):
                cls.run(args, architecture, configuration)
            return True
        except Exception:
            logging.getLogger("root").exception("process exception")
            return False

    @classmethod
    def execute(cls: Type[Handler], args: argparse.Namespace) -> int:
        """
        execute function for all aru
        :param args: command line args
        :return: 0 on success, 1 otherwise
        """
        architectures = cls.extract_architectures(args)
        with Pool(len(architectures)) as pool:
            result = pool.starmap(
                cls._call, [(args, architecture) for architecture in set(architectures)])
        return 0 if all(result) else 1

    @classmethod
    def extract_architectures(cls: Type[Handler], args: argparse.Namespace) -> List[str]:
        """
        get known architectures
        :param args: command line args
        :return: list of architectures for which tree is created
        """
        if args.architecture is None:
            raise MissingArchitecture(args.command)
        if args.architecture:
            architectures: List[str] = args.architecture  # avoid mypy warning
            return architectures

        config = Configuration()
        config.load(args.configuration)
        root = config.getpath("repository", "root")
        return RepositoryPaths.known_architectures(root)

    @classmethod
    def run(cls: Type[Handler], args: argparse.Namespace, architecture: str, configuration: Configuration) -> None:
        """
        callback for command line
        :param args: command line args
        :param architecture: repository architecture
        :param configuration: configuration instance
        """
        raise NotImplementedError
