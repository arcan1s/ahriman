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
import os

from typing import Optional

from ahriman.core.exceptions import DuplicateRun


class Lock:

    def __init__(self, path: Optional[str], force: bool) -> None:
        self.path = path
        self.force = force

    def __enter__(self):
        if self.force:
            self.remove()
        self.check()
        self.create()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.remove()

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