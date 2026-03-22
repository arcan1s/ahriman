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
from collections.abc import Callable
from typing import Any

from ahriman import __version__
from ahriman.core.auth.helpers import authorized_userid
from ahriman.core.types import Comparable
from ahriman.core.utils import pretty_interval
from ahriman.web.apispec import aiohttp_apispec
from ahriman.web.views.base import BaseView


__all__ = ["server_info"]


async def server_info(view: BaseView) -> dict[str, Any]:
    """
    generate server info which can be used in responses directly

    Args:
        view(BaseView): view of the request

    Returns:
        dict[str, Any]: server info as a JSON response
    """
    autorefresh_intervals = [
        {
            "interval": interval * 1000,  # milliseconds
            "is_active": index == 0,  # first element is always default
            "text": pretty_interval(interval),
        }
        for index, interval in enumerate(view.configuration.getintlist("web", "autorefresh_intervals", fallback=[]))
        if interval > 0  # special case if 0 exists and first, refresh will not be turned on by default
    ]
    comparator: Callable[[dict[str, Any]], Comparable] = lambda interval: interval["interval"]

    return {
        "auth": {
            "control": view.validator.auth_control,
            "enabled": view.validator.enabled,
            "external": view.validator.is_external,
            "username": await authorized_userid(view.request),
        },
        "autorefresh_intervals": sorted(autorefresh_intervals, key=comparator),
        "docs_enabled": aiohttp_apispec is not None,
        "index_url": view.configuration.get("web", "index_url", fallback=None),
        "repositories": [
            {
                "id": repository_id.id,
                **repository_id.view(),
            }
            for repository_id in sorted(view.services)
        ],
        "version": __version__,
    }
