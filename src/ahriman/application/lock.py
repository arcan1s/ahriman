#
# Copyright (c) 2021-2024 ahriman team.
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
import fcntl
import os

from io import TextIOWrapper
from pathlib import Path
from types import TracebackType
from typing import Literal, Self

from ahriman import __version__
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import DuplicateRunError
from ahriman.core.log import LazyLogging
from ahriman.core.status import Client
from ahriman.core.util import check_user
from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.repository_id import RepositoryId
from ahriman.models.waiter import Waiter


class Lock(LazyLogging):
    """
    wrapper for application lock file. Credits for idea to https://github.com/bmhatfield/python-pidfile.git

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
        self.path: Path | None = None
        if args.lock is not None:
            self.path = args.lock.with_stem(f"{args.lock.stem}_{repository_id.id}")
            if not self.path.is_absolute():
                # prepend full path to the lock file
                self.path = Path("/") / "run" / "ahriman" / self.path
        self._pid_file: TextIOWrapper | None = None

        self.force: bool = args.force
        self.unsafe: bool = args.unsafe
        self.wait_timeout: int = args.wait_timeout

        self.paths = configuration.repository_paths
        self.reporter = Client.load(repository_id, configuration, report=args.report)

    @staticmethod
    def perform_lock(fd: int) -> bool:
        """
        perform file lock

        Args:
            fd(int): file descriptor:

        Returns:
            bool: True in case if file is locked and False otherwise
        """
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return False

        return True

    def _open(self) -> None:
        """
        create lock file
        """
        if self.path is None:
            return
        self._pid_file = self.path.open("a+")

    def _watch(self) -> None:
        """
        watch until lock disappear
        """
        # there are reasons why we are not using inotify here. First of all, if we would use it, it would bring to
        # race conditions because multiple processes will be notified at the same time. Secondly, it is good library,
        # but platform-specific, and we only need to check if file exists
        if self._pid_file is None:
            return

        waiter = Waiter(self.wait_timeout)
        waiter.wait(lambda fd: not self.perform_lock(fd), self._pid_file.fileno())

    def _write(self) -> None:
        """
        write pid to the lock file

        Raises:
            DuplicateRunError: if it cannot lock PID file
        """
        if self._pid_file is None:
            return
        if not self.perform_lock(self._pid_file.fileno()):
            raise DuplicateRunError

        self._pid_file.seek(0)  # reset position and remove file content if any
        self._pid_file.truncate()

        self._pid_file.write(str(os.getpid()))  # write current pid
        self._pid_file.flush()  # flush data to disk

        self._pid_file.seek(0)  # reset position again

    def check_user(self) -> None:
        """
        check if current user is actually owner of ahriman root
        """
        check_user(self.paths, unsafe=self.unsafe)
        self.paths.tree_create()

    def check_version(self) -> None:
        """
        check web server version
        """
        status = self.reporter.status_get()
        if status.version is not None and status.version != __version__:
            self.logger.warning("status watcher version mismatch, our %s, their %s",
                                __version__, status.version)

    def clear(self) -> None:
        """
        remove lock file
        """
        if self._pid_file is not None:  # close file descriptor
            try:
                self._pid_file.close()
            except IOError:
                pass  # suppress any IO errors occur
        if self.path is not None:  # remove lock file
            self.path.unlink(missing_ok=True)

    def lock(self) -> None:
        """
        create pid file
        """
        if self.force:  # remove lock if force flag is set
            self.clear()
        self._open()
        self._watch()
        self._write()

    def __enter__(self) -> Self:
        """
        default workflow is the following:

            #. Check user UID
            #. Check web status watcher status
            #. Open lock file
            #. Wait for lock file to be free
            #. Write current PID to the lock file
            #. Report to status page if enabled

        Returns:
            Self: always instance of self
        """
        self.check_user()
        self.check_version()
        self.lock()
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
