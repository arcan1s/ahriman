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

from dataclasses import dataclass, field


@dataclass(frozen=True)
class LogRecordId:
    """
    log record process identifier

    Attributes:
        package_base(str): package base for which log record belongs
        version(str): package version for which log record belongs
        process_id(str, optional): unique process identifier
    """

    package_base: str
    version: str

    # this is not mistake, this value is kind of global identifier, which is generated
    # upon the process start
    process_id: str = field(default=str(uuid.uuid4()))
