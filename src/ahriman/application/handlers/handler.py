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
import logging

from collections.abc import Iterable
from multiprocessing import Pool

from ahriman.application.lock import Lock
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import ExitCode, MissingArchitectureError, MultipleArchitecturesError
from ahriman.core.log.log_loader import LogLoader
from ahriman.models.repository_id import RepositoryId
from ahriman.models.repository_paths import RepositoryPaths


class Handler:
    """
    base handler class for command callbacks

    Attributes:
        ALLOW_MULTI_ARCHITECTURE_RUN(bool): (class attribute) allow running with multiple architectures

    Examples:
        Wrapper for all command line actions, though each derived class implements ``run`` method, it usually must not
        be called directly. The recommended way is to call ``execute`` class method, e.g.::

            >>> from ahriman.application.handlers import Add
            >>>
            >>> Add.execute(args)
    """

    ALLOW_MULTI_ARCHITECTURE_RUN = True

    @classmethod
    def call(cls, args: argparse.Namespace, repository_id: RepositoryId) -> bool:
        """
        additional function to wrap all calls for multiprocessing library

        Args:
            args(argparse.Namespace): command line args
            repository_id(RepositoryId): repository unique identifier

        Returns:
            bool: True on success, False otherwise
        """
        try:
            configuration = Configuration.from_path(args.configuration, repository_id)

            log_handler = LogLoader.handler(args.log_handler)
            LogLoader.load(repository_id, configuration, log_handler, quiet=args.quiet, report=args.report)

            with Lock(args, repository_id, configuration):
                cls.run(args, repository_id, configuration, report=args.report)

            return True
        except ExitCode:
            return False
        except Exception:
            # we are basically always want to print error to stderr instead of default logger
            logging.getLogger("stderr").exception("process exception")
            return False

    @classmethod
    def execute(cls, args: argparse.Namespace) -> int:
        """
        execute function for all aru

        Args:
            args(argparse.Namespace): command line args

        Returns:
            int: 0 on success, 1 otherwise

        Raises:
            MultipleArchitecturesError: if more than one architecture supplied and no multi architecture supported
        """
        repositories = cls.repositories_extract(args)

        # actually we do not have to spawn another process if it is single-process application, do we?
        if len(repositories) > 1:
            if not cls.ALLOW_MULTI_ARCHITECTURE_RUN:
                raise MultipleArchitecturesError(args.command, repositories)

            with Pool(len(repositories)) as pool:
                result = pool.starmap(cls.call, [(args, repository_id) for repository_id in repositories])
        else:
            result = [cls.call(args, repositories.pop())]

        return 0 if all(result) else 1

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
            raise ExitCode

    @staticmethod
    def repositories_extract(args: argparse.Namespace) -> list[RepositoryId]:
        """
        get known architectures

        Args:
            args(argparse.Namespace): command line args

        Returns:
            list[RepositoryId]: list of repository names and architectures for which tree is created

        Raises:
            MissingArchitectureError: if no architecture set and automatic detection is not allowed or failed
        """
        configuration = Configuration()
        configuration.load(args.configuration)
        # pylint, wtf???
        root = configuration.getpath("repository", "root")  # pylint: disable=assignment-from-no-return

        # preparse systemd repository-id argument
        # we are using unescaped values, so / is not allowed here, because it is impossible to separate if from dashes
        if args.repository_id is not None:
            separator = "/" if "/" in args.repository_id else "-"  # systemd and non-systemd identifiers
            # repository parts is optional for backward compatibility
            architecture, *repository_parts = args.repository_id.split(separator)  # maxsplit isn't used intentionally
            args.architecture = architecture
            if repository_parts:
                args.repository = "-".join(repository_parts)  # replace slash with dash

        # extract repository names first
        if (from_args := args.repository) is not None:
            repositories: Iterable[str] = [from_args]
        elif (from_filesystem := RepositoryPaths.known_repositories(root)):
            repositories = from_filesystem
        else:  # try to read configuration now
            repositories = [configuration.get("repository", "name")]

        # extract architecture names
        if (architecture := args.architecture) is not None:
            parsed = set(
                RepositoryId(architecture, repository)
                for repository in repositories
            )
        else:  # try to read from file system
            parsed = set(
                RepositoryId(architecture, repository)
                for repository in repositories
                for architecture in RepositoryPaths.known_architectures(root, repository)
            )

        if not parsed:
            raise MissingArchitectureError(args.command)
        return sorted(parsed)
