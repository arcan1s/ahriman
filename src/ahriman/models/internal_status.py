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
from dataclasses import dataclass, field
from typing import Any, Self

from ahriman.core.utils import dataclass_view
from ahriman.models.build_status import BuildStatus
from ahriman.models.counters import Counters
from ahriman.models.repository_stats import RepositoryStats


@dataclass(frozen=True, kw_only=True)
class InternalStatus:
    """
    internal server status

    Attributes:
        status(BuildStatus): service status
        architecture(str | None): repository architecture
        packages(Counters): packages statuses counter object
        repository(str | None): repository name
        stats(RepositoryStats | None): repository stats
        version(str | None): service version
    """

    status: BuildStatus
    architecture: str | None = None
    packages: Counters = field(default=Counters(total=0))
    repository: str | None = None
    stats: RepositoryStats | None = None
    version: str | None = None

    @classmethod
    def from_json(cls, dump: dict[str, Any]) -> Self:
        """
        construct internal status from json dump

        Args:
            dump(dict[str, Any]): json dump body

        Returns:
            Self: internal status
        """
        counters = Counters.from_json(dump["packages"]) if "packages" in dump else Counters(total=0)
        stats = RepositoryStats.from_json(dump["stats"]) if "stats" in dump else None
        build_status = dump.get("status") or {}
        return cls(status=BuildStatus.from_json(build_status),
                   architecture=dump.get("architecture"),
                   packages=counters,
                   repository=dump.get("repository"),
                   stats=stats,
                   version=dump.get("version"))

    def view(self) -> dict[str, Any]:
        """
        generate json status view

        Returns:
            dict[str, Any]: json-friendly dictionary
        """
        return dataclass_view(self)
