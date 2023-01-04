#
# Copyright (c) 2021-2023 ahriman team.
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

from dataclasses import dataclass, fields
from typing import Any, Dict, List, Tuple, Type

from ahriman.core.util import filter_json
from ahriman.models.build_status import BuildStatus
from ahriman.models.package import Package


@dataclass(frozen=True, kw_only=True)
class Counters:
    """
    package counters

    Attributes:
        total(int): total packages count
        unknown(int): packages in unknown status count
        pending(int): packages in pending status count
        building(int): packages in building status count
        failed(int): packages in failed status count
        success(int): packages in success status count
    """

    total: int
    unknown: int = 0
    pending: int = 0
    building: int = 0
    failed: int = 0
    success: int = 0

    @classmethod
    def from_json(cls: Type[Counters], dump: Dict[str, Any]) -> Counters:
        """
        construct counters from json dump

        Args:
            dump(Dict[str, Any]): json dump body

        Returns:
            Counters: status counters
        """
        # filter to only known fields
        known_fields = [pair.name for pair in fields(cls)]
        return cls(**filter_json(dump, known_fields))

    @classmethod
    def from_packages(cls: Type[Counters], packages: List[Tuple[Package, BuildStatus]]) -> Counters:
        """
        construct counters from packages statuses

        Args:
            packages(List[Tuple[Package, BuildStatus]]): list of package and their status as per watcher property

        Returns:
            Counters: status counters
        """
        per_status = {"total": len(packages)}
        for _, status in packages:
            key = status.status.name.lower()
            per_status.setdefault(key, 0)
            per_status[key] += 1
        return cls(**per_status)
