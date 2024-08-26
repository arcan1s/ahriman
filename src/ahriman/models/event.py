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
from dataclasses import dataclass, field, fields
from enum import StrEnum
from typing import Any, Self

from ahriman.core.utils import dataclass_view, filter_json, utcnow


class EventType(StrEnum):
    """
    predefined event types

    Attributes:
        PackageOutdated(EventType): (class attribute) package has been marked as out-of-date
        PackageRemoved(EventType): (class attribute) package has been removed
        PackageUpdateFailed(EventType): (class attribute) package update has been failed
        PackageUpdated(EventType): (class attribute) package has been updated
    """

    PackageOutdated = "package-outdated"
    PackageRemoved = "package-removed"
    PackageUpdateFailed = "package-update-failed"
    PackageUpdated = "package-updated"


@dataclass(frozen=True)
class Event:
    """
    audit log event

    Attributes:
        created(int): event timestamp
        data(dict[str, Any]): event metadata
        event(str | EventType): event type
        message(str | None): event message if available
        object_id(str): object identifier
    """

    event: str | EventType
    object_id: str
    message: str | None = None
    data: dict[str, Any] = field(default_factory=dict)
    created: int = field(default_factory=lambda: int(utcnow().timestamp()))

    def __post_init__(self) -> None:
        """
        convert event type to enum if it is a well-known event type
        """
        if self.event in EventType:
            object.__setattr__(self, "event", EventType(self.event))

    @classmethod
    def from_json(cls, dump: dict[str, Any]) -> Self:
        """
        construct event from the json dump

        Args:
            dump(dict[str, Any]): json dump body

        Returns:
            Self: dependencies object
        """
        # filter to only known fields
        known_fields = [pair.name for pair in fields(cls)]
        return cls(**filter_json(dump, known_fields))

    def view(self) -> dict[str, Any]:
        """
        generate json event view

        Returns:
            dict[str, Any]: json-friendly dictionary
        """
        return dataclass_view(self)
