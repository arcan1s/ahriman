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

from pathlib import Path
from types import TracebackType
from typing import Literal, Optional, Type

from ahriman import version
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import DuplicateRun
from ahriman.core.status.client import Client
from ahriman.core.util import check_user
from ahriman.models.build_status import BuildStatusEnum


class Lock:
    """
    wrapper for application lock file
    :ivar force: remove lock file on start if any
    :ivar path: path to lock file if any
    :ivar reporter: build status reporter instance
    :ivar root: repository root (i.e. ahriman home)
    :ivar unsafe: skip user check
    """

    def __init__(self, args: argparse.Namespace, architecture: str, configuration: Configuration) -> None:
        """
        default constructor
        :param args: command line args
        :param architecture: repository architecture
        :param configuration: configuration instance
        """
        self.path = Path(f"{args.lock}_{architecture}") if args.lock is not None else None
        self.force = args.force
        self.unsafe = args.unsafe

        self.root = Path(configuration.get("repository", "root"))
        self.reporter = Client() if args.no_report else Client.load(configuration)

    def __enter__(self) -> Lock:
        """
        default workflow is the following:

            check user UID
            check if there is lock file
            check web status watcher status
            create lock file
            report to web if enabled
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
        :param exc_type: exception type name if any
        :param exc_val: exception raised if any
        :param exc_tb: exception traceback if any
        :return: always False (do not suppress any exception)
        """
        self.clear()
        status = BuildStatusEnum.Success if exc_val is None else BuildStatusEnum.Failed
        self.reporter.update_self(status)
        return False

    def check_version(self) -> None:
        """
        check web server version
        """
        status = self.reporter.get_internal()
        if status.version is not None and status.version != version.__version__:
            logging.getLogger("root").warning(
                "status watcher version mismatch, our %s, their %s",
                version.__version__,
                status.version)

    def check_user(self) -> None:
        """
        check if current user is actually owner of ahriman root
        """
        check_user(self.root, self.unsafe)

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
        """
        if self.path is None:
            return
        try:
            self.path.touch(exist_ok=self.force)
        except FileExistsError:
            raise DuplicateRun()
