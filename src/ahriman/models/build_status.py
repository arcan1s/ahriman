#
# Copyright (c) 2021-2022 ahriman team.
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

from dataclasses import dataclass, field, fields
from enum import Enum
from typing import Any, Dict, Type

from ahriman.core.util import filter_json, pretty_datetime, utcnow


class BuildStatusEnum(str, Enum):
    """
    build status enumeration

    Attributes:
        Unknown(BuildStatusEnum): (class attribute) build status is unknown
        Pending(BuildStatusEnum): (class attribute) package is out-of-dated and will be built soon
        Building(BuildStatusEnum): (class attribute) package is building right now
        Failed(BuildStatusEnum): (class attribute) package build failed
        Success(BuildStatusEnum): (class attribute) package has been built without errors
    """

    Unknown = "unknown"
    Pending = "pending"
    Building = "building"
    Failed = "failed"
    Success = "success"


@dataclass(frozen=True)
class BuildStatus:
    """
    build status holder

    Attributes:
        status(BuildStatusEnum): build status
        timestamp(int): build status update time
    """

    status: BuildStatusEnum = BuildStatusEnum.Unknown
    timestamp: int = field(default_factory=lambda: int(utcnow().timestamp()))

    def __post_init__(self) -> None:
        """
        convert status to enum type
        """
        object.__setattr__(self, "status", BuildStatusEnum(self.status))

    @classmethod
    def from_json(cls: Type[BuildStatus], dump: Dict[str, Any]) -> BuildStatus:
        """
        construct status properties from json dump

        Args:
            dump(Dict[str, Any]): json dump body

        Returns:
            BuildStatus: status properties
        """
        known_fields = [pair.name for pair in fields(cls)]
        return cls(**filter_json(dump, known_fields))

    def pretty_print(self) -> str:
        """
        generate pretty string representation

        Returns:
            str: print-friendly string
        """
        return f"{self.status.value} ({pretty_datetime(self.timestamp)})"

    def view(self) -> Dict[str, Any]:
        """
        generate json status view

        Returns:
            Dict[str, Any]: json-friendly dictionary
        """
        return {
            "status": self.status.value,
            "timestamp": self.timestamp
        }
