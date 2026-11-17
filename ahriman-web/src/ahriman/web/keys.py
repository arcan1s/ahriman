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
from aiohttp.web import AppKey

from ahriman.core.auth import Auth
from ahriman.core.configuration import Configuration
from ahriman.core.distributed import WorkersCache
from ahriman.core.spawn import Spawn
from ahriman.core.status.watcher import Watcher
from ahriman.models.repository_id import RepositoryId


__all__ = [
    "AUTH_KEY",
    "CONFIGURATION_KEY",
    "SPAWN_KEY",
    "WATCHER_KEY",
    "WORKERS_KEY",
]


AUTH_KEY = AppKey("validator", Auth)
CONFIGURATION_KEY = AppKey("configuration", Configuration)
SPAWN_KEY = AppKey("spawn", Spawn)
WATCHER_KEY = AppKey("watcher", dict[RepositoryId, Watcher])
WORKERS_KEY = AppKey("workers", WorkersCache)
