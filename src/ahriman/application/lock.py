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

from ahriman.core.exceptions import DuplicateRun


class Lock:

    def __init__(self, path: Optional[str], architecture: str, force: bool) -> None:
        self.path = f'{path}_{architecture}' if path is not None else None
        self.force = force

    def __enter__(self) -> Lock:
        if self.force:
            self.remove()
        self.check()
        self.create()
        return self

    def __exit__(self, exc_type: Optional[Type[Exception]], exc_val: Optional[Exception],
                 exc_tb: TracebackType) -> Literal[False]:
        self.remove()
        return False

    def check(self) -> None:
        if self.path is None:
            return
        if os.path.exists(self.path):
            raise DuplicateRun()

    def create(self) -> None:
        if self.path is None:
            return
        open(self.path, 'w').close()

    def remove(self) -> None:
        if self.path is None:
            return
        if os.path.exists(self.path):
            os.remove(self.path)