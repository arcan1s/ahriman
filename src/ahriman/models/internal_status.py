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

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional, Type

from ahriman.models.counters import Counters


@dataclass
class InternalStatus:
    """
    internal server status
    :ivar architecture: repository architecture
    :ivar packages: packages statuses counter object
    :ivar repository: repository name
    :ivar version: service version
    """

    architecture: Optional[str] = None
    packages: Counters = field(default=Counters(total=0))
    repository: Optional[str] = None
    version: Optional[str] = None

    @classmethod
    def from_json(cls: Type[InternalStatus], dump: Dict[str, Any]) -> InternalStatus:
        """
        construct internal status from json dump
        :param dump: json dump body
        :return: internal status
        """
        counters = Counters.from_json(dump["packages"]) if "packages" in dump else Counters(total=0)
        return cls(architecture=dump.get("architecture"),
                   packages=counters,
                   repository=dump.get("repository"),
                   version=dump.get("version"))

    def view(self) -> Dict[str, Any]:
        """
        generate json status view
        :return: json-friendly dictionary
        """
        return asdict(self)
