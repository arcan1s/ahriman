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

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional, Type

from ahriman.models.build_status import BuildStatus
from ahriman.models.counters import Counters


@dataclass(frozen=True, kw_only=True)
class InternalStatus:
    """
    internal server status

    Attributes:
        status(BuildStatus): service status
        architecture(Optional[str]): repository architecture
        packages(Counters): packages statuses counter object
        repository(Optional[str]): repository name
        version(Optional[str]): service version
    """

    status: BuildStatus
    architecture: Optional[str] = None
    packages: Counters = field(default=Counters(total=0))
    repository: Optional[str] = None
    version: Optional[str] = None

    @classmethod
    def from_json(cls: Type[InternalStatus], dump: Dict[str, Any]) -> InternalStatus:
        """
        construct internal status from json dump

        Args:
            dump(Dict[str, Any]): json dump body

        Returns:
            InternalStatus: internal status
        """
        counters = Counters.from_json(dump["packages"]) if "packages" in dump else Counters(total=0)
        build_status = dump.get("status") or {}
        return cls(status=BuildStatus.from_json(build_status),
                   architecture=dump.get("architecture"),
                   packages=counters,
                   repository=dump.get("repository"),
                   version=dump.get("version"))

    def view(self) -> Dict[str, Any]:
        """
        generate json status view

        Returns:
            Dict[str, Any]: json-friendly dictionary
        """
        return asdict(self)
