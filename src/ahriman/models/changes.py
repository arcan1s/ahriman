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
from dataclasses import dataclass, fields
from typing import Any, Self

from ahriman.core.utils import dataclass_view, filter_json


@dataclass(frozen=True)
class Changes:
    """
    package source files changes holder

    Attributes:
        last_commit_sha(str | None): last commit hash
        changes(str | None): package change since the last commit if available
    """

    last_commit_sha: str | None = None
    changes: str | None = None

    @property
    def is_empty(self) -> bool:
        """
        validate that changes are not empty

        Returns:
            bool: ``True`` in case if changes are not set and ``False`` otherwise
        """
        return self.changes is None

    @classmethod
    def from_json(cls, dump: dict[str, Any]) -> Self:
        """
        construct changes from the json dump

        Args:
            dump(dict[str, Any]): json dump body

        Returns:
            Self: changes object
        """
        # filter to only known fields
        known_fields = [pair.name for pair in fields(cls)]
        return cls(**filter_json(dump, known_fields))

    def view(self) -> dict[str, Any]:
        """
        generate json change view

        Returns:
            dict[str, Any]: json-friendly dictionary
        """
        return dataclass_view(self)
