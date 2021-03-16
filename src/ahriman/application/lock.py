#
# Copyright (c) 2021 Evgenii Alekseev.
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

import os

from types import TracebackType
from typing import Literal, Optional, Type

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import DuplicateRun, UnsafeRun
from ahriman.core.watcher.client import Client
from ahriman.models.build_status import BuildStatusEnum


class Lock:
    '''
    wrapper for application lock file
    :ivar force: remove lock file on start if any
    :ivar path: path to lock file if any
    :ivar reporter: build status reporter instance
    :ivar root: repository root (i.e. ahriman home)
    :ivar unsafe: skip user check
    '''

    def __init__(self, path: Optional[str], architecture: str, force: bool, unsafe: bool,
                 config: Configuration) -> None:
        '''
        default constructor
        :param path: optional path to lock file, if empty no file lock will be used
        :param architecture: repository architecture
        :param force: remove lock file on start if any
        :param unsafe: skip user check
        :param config: configuration instance
        '''
        self.path = f'{path}_{architecture}' if path is not None else None
        self.force = force
        self.unsafe = unsafe

        self.root = config.get('repository', 'root')
        self.reporter = Client.load(architecture, config)

    def __enter__(self) -> Lock:
        '''
        default workflow is the following:

            check user UID
            remove lock file if force flag is set
            check if there is lock file
            create lock file
            report to web if enabled
        '''
        self.check_user()
        if self.force:
            self.remove()
        self.check()
        self.create()
        self.reporter.update_self(BuildStatusEnum.Building)
        return self

    def __exit__(self, exc_type: Optional[Type[Exception]], exc_val: Optional[Exception],
                 exc_tb: TracebackType) -> Literal[False]:
        '''
        remove lock file when done
        :param exc_type: exception type name if any
        :param exc_val: exception raised if any
        :param exc_tb: exception traceback if any
        :return: always False (do not suppress any exception)
        '''
        self.remove()
        status = BuildStatusEnum.Success if exc_val is None else BuildStatusEnum.Failed
        self.reporter.update_self(status)
        return False

    def check(self) -> None:
        '''
        check if lock file exists, raise exception if it does
        '''
        if self.path is None:
            return
        if os.path.exists(self.path):
            raise DuplicateRun()

    def check_user(self) -> None:
        '''
        check if current user is actually owner of ahriman root
        '''
        if self.unsafe:
            return
        current_uid = os.getuid()
        root_uid = os.stat(self.root).st_uid
        if current_uid != root_uid:
            raise UnsafeRun(current_uid, root_uid)

    def create(self) -> None:
        '''
        create lock file
        '''
        if self.path is None:
            return
        open(self.path, 'w').close()

    def remove(self) -> None:
        '''
        remove lock file
        '''
        if self.path is None:
            return
        if os.path.exists(self.path):
            os.remove(self.path)
