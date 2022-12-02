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
from ahriman.core.exceptions import ExitCode, MissingArchitectureError, MultipleArchitecturesError
from ahriman.core.log import Log
from ahriman.models.repository_paths import RepositoryPaths


class Handler:
    """
    base handler class for command callbacks

    Attributes:
        ALLOW_AUTO_ARCHITECTURE_RUN(bool): (class attribute) allow defining architecture from existing repositories
        ALLOW_MULTI_ARCHITECTURE_RUN(bool): (class attribute) allow running with multiple architectures

    Examples:
        Wrapper for all command line actions, though each derived class implements ``run`` method, it usually must not
        be called directly. The recommended way is to call ``execute`` class method, e.g.::

            >>> from ahriman.application.handlers import Add
            >>>
            >>> Add.execute(args)
    """

    ALLOW_AUTO_ARCHITECTURE_RUN = True
    ALLOW_MULTI_ARCHITECTURE_RUN = True

    @classmethod
    def architectures_extract(cls: Type[Handler], args: argparse.Namespace) -> List[str]:
        """
        get known architectures

        Args:
            args(argparse.Namespace): command line args

        Returns:
            List[str]: list of architectures for which tree is created

        Raises:
            MissingArchitecture: if no architecture set and automatic detection is not allowed or failed
        """
        if not cls.ALLOW_AUTO_ARCHITECTURE_RUN and args.architecture is None:
            # for some parsers (e.g. config) we need to run with specific architecture
            # for those cases architecture must be set explicitly
            raise MissingArchitectureError(args.command)
        if args.architecture:  # architecture is specified explicitly
            return sorted(set(args.architecture))

        configuration = Configuration()
        configuration.load(args.configuration)
        # wtf???
        root = configuration.getpath("repository", "root")  # pylint: disable=assignment-from-no-return
        architectures = RepositoryPaths.known_architectures(root)

        if not architectures:  # well we did not find anything
            raise MissingArchitectureError(args.command)
        return sorted(architectures)

    @classmethod
    def call(cls: Type[Handler], args: argparse.Namespace, architecture: str) -> bool:
        """
        additional function to wrap all calls for multiprocessing library

        Args:
            args(argparse.Namespace): command line args
            architecture(str): repository architecture

        Returns:
            bool: True on success, False otherwise
        """
        try:
            configuration = Configuration.from_path(args.configuration, architecture)
            Log.load(configuration, quiet=args.quiet, report=args.report)
            with Lock(args, architecture, configuration):
                cls.run(args, architecture, configuration, report=args.report, unsafe=args.unsafe)
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

        Args:
            args(argparse.Namespace): command line args

        Returns:
            int: 0 on success, 1 otherwise

        Raises:
            MultipleArchitectures: if more than one architecture supplied and no multi architecture supported
        """
        architectures = cls.architectures_extract(args)

        # actually we do not have to spawn another process if it is single-process application, do we?
        if len(architectures) > 1:
            if not cls.ALLOW_MULTI_ARCHITECTURE_RUN:
                raise MultipleArchitecturesError(args.command)

            with Pool(len(architectures)) as pool:
                result = pool.starmap(
                    cls.call, [(args, architecture) for architecture in architectures])
        else:
            result = [cls.call(args, architectures.pop())]

        return 0 if all(result) else 1

    @classmethod
    def run(cls: Type[Handler], args: argparse.Namespace, architecture: str, configuration: Configuration, *,
            report: bool, unsafe: bool) -> None:
        """
        callback for command line

        Args:
            args(argparse.Namespace): command line args
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
            report(bool): force enable or disable reporting
            unsafe(bool): if set no user check will be performed before path creation

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    @staticmethod
    def check_if_empty(enabled: bool, predicate: bool) -> None:
        """
        check condition and flag and raise ExitCode exception in case if it is enabled and condition match

        Args:
            enabled(bool): if False no check will be performed
            predicate(bool): indicates condition on which exception should be thrown

        Raises:
            ExitCode: if result is empty and check is enabled
        """
        if enabled and predicate:
            raise ExitCode()
