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

from pathlib import Path
from types import TracebackType
from typing import Literal, Self

from ahriman import __version__
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import DuplicateRunError
from ahriman.core.log import LazyLogging
from ahriman.core.status.client import Client
from ahriman.core.util import check_user
from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.repository_id import RepositoryId
from ahriman.models.waiter import Waiter


class Lock(LazyLogging):
    """
    wrapper for application lock file

    Attributes:
        force(bool): remove lock file on start if any
        path(Path): path to lock file if any
        reporter(Client): build status reporter instance
        paths(RepositoryPaths): repository paths instance
        unsafe(bool): skip user check
        wait_timeout(int): wait in seconds until lock will free

    Examples:
        Instance of this class except for controlling file-based lock is also required for basic applications checks.
        The common flow is to create instance in ``with`` block and handle exceptions after all::

            >>> from ahriman.core.configuration import Configuration
            >>> from ahriman.models.repository_id import RepositoryId
            >>>
            >>> configuration = Configuration()
            >>> try:
            >>>     with Lock(args, RepositoryId("x86_64", "aur-clone"), configuration):
            >>>         perform_actions()
            >>> except Exception as exception:
            >>>     handle_exceptions(exception)
    """

    def __init__(self, args: argparse.Namespace, repository_id: RepositoryId, configuration: Configuration) -> None:
        """
        default constructor

        Args:
            args(argparse.Namespace): command line args
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
        """
        lock_suffix = f"{repository_id.name}_{repository_id.architecture}"
        self.path: Path | None = \
            args.lock.with_stem(f"{args.lock.stem}_{lock_suffix}") if args.lock is not None else None

        self.force: bool = args.force
        self.unsafe: bool = args.unsafe
        self.wait_timeout: int = args.wait_timeout

        self.paths = configuration.repository_paths
        self.reporter = Client.load(configuration, report=args.report)

    def check_version(self) -> None:
        """
        check web server version
        """
        status = self.reporter.status_get()
        if status.version is not None and status.version != __version__:
            self.logger.warning("status watcher version mismatch, our %s, their %s",
                                __version__, status.version)

    def check_user(self) -> None:
        """
        check if current user is actually owner of ahriman root
        """
        check_user(self.paths, unsafe=self.unsafe)
        self.paths.tree_create()

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
            DuplicateRunError: if lock exists and no force flag supplied
        """
        if self.path is None:
            return
        try:
            self.path.touch(exist_ok=self.force)
        except FileExistsError:
            raise DuplicateRunError from None

    def watch(self) -> None:
        """
        watch until lock disappear
        """
        # there are reasons why we are not using inotify here. First of all, if we would use it, it would bring to
        # race conditions because multiple processes will be notified in the same time. Secondly, it is good library,
        # but platform-specific, and we only need to check if file exists
        if self.path is None:
            return

        waiter = Waiter(self.wait_timeout)
        waiter.wait(self.path.is_file)

    def __enter__(self) -> Self:
        """
        default workflow is the following:

            1. Check user UID
            2. Check if there is lock file
            3. Check web status watcher status
            4. Wait for lock file to be free
            5. Create lock file and directory tree
            6. Report to status page if enabled

        Returns:
            Self: always instance of self
        """
        self.check_user()
        self.check_version()
        self.watch()
        self.create()
        self.reporter.status_update(BuildStatusEnum.Building)
        return self

    def __exit__(self, exc_type: type[Exception] | None, exc_val: Exception | None,
                 exc_tb: TracebackType) -> Literal[False]:
        """
        remove lock file when done

        Args:
            exc_type(type[Exception] | None): exception type name if any
            exc_val(Exception | None): exception raised if any
            exc_tb(TracebackType): exception traceback if any

        Returns:
            Literal[False]: always False (do not suppress any exception)
        """
        self.clear()
        status = BuildStatusEnum.Success if exc_val is None else BuildStatusEnum.Failed
        self.reporter.status_update(status)
        return False
