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
from typing import Type

from ahriman.application.lock import Lock
from ahriman.core.configuration import Configuration


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
        with Pool(len(args.architecture)) as pool:
            result = pool.starmap(
                cls._call, [(args, architecture) for architecture in set(args.architecture)])
        return 0 if all(result) else 1

    @classmethod
    def run(cls: Type[Handler], args: argparse.Namespace, architecture: str, configuration: Configuration) -> None:
        """
        callback for command line
        :param args: command line args
        :param architecture: repository architecture
        :param configuration: configuration instance
        """
        raise NotImplementedError
