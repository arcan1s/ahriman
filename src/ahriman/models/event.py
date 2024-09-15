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
from enum import StrEnum
from typing import Any, Self

from ahriman.core.utils import utcnow


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

    def __init__(self, event: str | EventType, object_id: str, message: str | None = None, created: int | None = None,
                 **kwargs: Any):
        """
        Args:
            event(str | EventType): event type
            object_id(str): object identifier
            message(str | None): event message if available
            created(int | None, optional): event timestamp (Default value = None)
            **kwargs(Any): event metadata
        """
        self.event = EventType(event) if event in EventType else event
        self.object_id = object_id
        self.created = created or int(utcnow().timestamp())

        self.message = message
        self.data = kwargs

    @classmethod
    def from_json(cls, dump: dict[str, Any]) -> Self:
        """
        construct event from the json dump

        Args:
            dump(dict[str, Any]): json dump body

        Returns:
            Self: dependencies object
        """
        return cls(
            event=dump["event"],
            object_id=dump["object_id"],
            message=dump.get("message"),
            created=dump.get("created"),
            **dump.get("data", {}),
        )

    def get(self, key: str) -> Any:
        """
        get a property

        Args:
            key(str): key to lookup in data

        Returns:
            Any: metadata property if available or ``None`` otherwise
        """
        return self.data.get(key)

    def view(self) -> dict[str, Any]:
        """
        generate json event view

        Returns:
            dict[str, Any]: json-friendly dictionary
        """
        dump = {
            "event": self.event,
            "object_id": self.object_id,
            "created": self.created,
        }
        if self.message is not None:
            dump["message"] = self.message
        if self.data:
            dump["data"] = self.data

        return dump

    def __eq__(self, other: Any) -> bool:
        """
        check if other is the same object

        Args:
            other(Any): other object instance

        Returns:
            bool: ``True`` if the other object is the same and ``False`` otherwise
        """
        if not isinstance(other, Event):
            return False
        return self.event == other.event \
            and self.object_id == other.object_id \
            and self.message == other.message \
            and self.created == other.created \
            and self.data == other.data
