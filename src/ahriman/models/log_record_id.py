#
# Copyright (c) 2021-2025 ahriman team.
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
import uuid

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class LogRecordId:
    """
    log record process identifier

    Attributes:
        DEFAULT_PROCESS_ID(str): (class attribute) default process identifier
        package_base(str): package base for which log record belongs
        version(str): package version for which log record belongs
        process_id(str, optional): unique process identifier
    """

    package_base: str
    version: str
    process_id: str = ""

    DEFAULT_PROCESS_ID: ClassVar[str] = str(uuid.uuid4())

    def __post_init__(self) -> None:
        """
        assign process identifier from default if not set
        """
        if not self.process_id:
            object.__setattr__(self, "process_id", self.DEFAULT_PROCESS_ID)
