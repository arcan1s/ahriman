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
from __future__ import annotations

import argparse

from pathlib import Path
from types import TracebackType
from typing import Literal, Optional, Type

from ahriman import version
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import DuplicateRunError
from ahriman.core.log import LazyLogging
from ahriman.core.status.client import Client
from ahriman.core.util import check_user
from ahriman.models.build_status import BuildStatusEnum


class Lock(LazyLogging):
    """
    wrapper for application lock file

    Attributes:
        force(bool): remove lock file on start if any
        path(Path): path to lock file if any
        reporter(Client): build status reporter instance
        paths(RepositoryPaths): repository paths instance
        unsafe(bool): skip user check

    Examples:
        Instance of this class except for controlling file-based lock is also required for basic applications checks.
        The common flow is to create instance in ``with`` block and handle exceptions after all::

            >>> from ahriman.core.configuration import Configuration
            >>>
            >>> configuration = Configuration()
            >>> try:
            >>>     with Lock(args, "x86_64", configuration):
            >>>         perform_actions()
            >>> except Exception as exception:
            >>>     handle_exceptions(exception)
    """

    def __init__(self, args: argparse.Namespace, architecture: str, configuration: Configuration) -> None:
        """
        default constructor

        Args:
            args(argparse.Namespace): command line args
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
        """
        self.path = Path(f"{args.lock}_{architecture}") if args.lock is not None else None
        self.force = args.force
        self.unsafe = args.unsafe

        self.paths = configuration.repository_paths
        self.reporter = Client.load(configuration, report=args.report)

    def check_version(self) -> None:
        """
        check web server version
        """
        status = self.reporter.get_internal()
        if status.version is not None and status.version != version.__version__:
            self.logger.warning("status watcher version mismatch, our %s, their %s",
                                version.__version__, status.version)

    def check_user(self) -> None:
        """
        check if current user is actually owner of ahriman root
        """
        check_user(self.paths, unsafe=self.unsafe)

    def clear(self) -> None:
        """
        remove lock file
        """
        if self.path is None:
            return
        self.path.unlink(missing_ok=True)

    def create(self) -> None:
        """
        create lock file

        Raises:
            DuplicateRun: if lock exists and no force flag supplied
        """
        if self.path is None:
            return
        try:
            self.path.touch(exist_ok=self.force)
        except FileExistsError:
            raise DuplicateRunError()

    def __enter__(self) -> Lock:
        """
        default workflow is the following:

            1. Check user UID
            2. Check if there is lock file
            3. Check web status watcher status
            4. Create lock file
            5. Report to status page if enabled
        """
        self.check_user()
        self.check_version()
        self.create()
        self.reporter.update_self(BuildStatusEnum.Building)
        return self

    def __exit__(self, exc_type: Optional[Type[Exception]], exc_val: Optional[Exception],
                 exc_tb: TracebackType) -> Literal[False]:
        """
        remove lock file when done

        Args:
            exc_type(Optional[Type[Exception]]): exception type name if any
            exc_val(Optional[Exception]): exception raised if any
            exc_tb(TracebackType): exception traceback if any

        Returns:
            Literal[False]: always False (do not suppress any exception)
        """
        self.clear()
        status = BuildStatusEnum.Success if exc_val is None else BuildStatusEnum.Failed
        self.reporter.update_self(status)
        return False
