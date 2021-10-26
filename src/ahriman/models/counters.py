#
# Copyright (c) 2021 ahriman team.
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


@dataclass
class Counters:
    """
    package counters
    :ivar total: total packages count
    :ivar unknown: packages in unknown status count
    :ivar pending: packages in pending status count
    :ivar building: packages in building status count
    :ivar failed: packages in failed status count
    :ivar success: packages in success status count
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
        :param dump: json dump body
        :return: status counters
        """
        # filter to only known fields
        known_fields = [pair.name for pair in fields(cls)]
        return cls(**filter_json(dump, known_fields))

    @classmethod
    def from_packages(cls: Type[Counters], packages: List[Tuple[Package, BuildStatus]]) -> Counters:
        """
        construct counters from packages statuses
        :param packages: list of package and their status as per watcher property
        :return: status counters
        """
        per_status = {"total": len(packages)}
        for _, status in packages:
            key = status.status.name.lower()
            per_status.setdefault(key, 0)
            per_status[key] += 1
        return cls(**per_status)
