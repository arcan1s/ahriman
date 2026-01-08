#
# Copyright (c) 2021-2026 ahriman team.
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
from dataclasses import dataclass
from typing import Any, Self

from ahriman.models.log_record_id import LogRecordId


@dataclass(frozen=True)
class LogRecord:
    """
    log record

    Attributes:
        log_record_id(LogRecordId): log record identifier
        created(float): log record creation timestamp
        message(str): log record message
    """

    log_record_id: LogRecordId
    created: float
    message: str

    @classmethod
    def from_json(cls, package_base: str, dump: dict[str, Any]) -> Self:
        """
        construct log record from the json dump

        Args:
            package_base(str): package base for which log record belongs
            dump(dict[str, Any]): json dump body

        Returns:
            Self: log record object
        """
        if "process_id" in dump:
            log_record_id = LogRecordId(package_base, dump["version"], dump["process_id"])
        else:
            log_record_id = LogRecordId(package_base, dump["version"])

        return cls(
            log_record_id=log_record_id,
            created=dump["created"],
            message=dump["message"],
        )

    def view(self) -> dict[str, Any]:
        """
        generate json log record view

        Returns:
            dict[str, Any]: json-friendly dictionary
        """
        return {
            "created": self.created,
            "message": self.message,
            "version": self.log_record_id.version,
            "process_id": self.log_record_id.process_id,
        }
