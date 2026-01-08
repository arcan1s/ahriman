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
try:
    import aiohttp_openmetrics
except ImportError:
    aiohttp_openmetrics = None  # type: ignore[assignment]

from aiohttp.typedefs import Middleware
from aiohttp.web import HTTPNotFound, Request, Response, StreamResponse, middleware

from ahriman.web.middlewares import HandlerType


__all__ = [
    "metrics",
    "metrics_handler",
]


async def metrics(request: Request) -> Response:
    """
    handler for returning metrics

    Args:
        request(Request): request object

    Returns:
        Response: response object

    Raises:
        HTTPNotFound: endpoint is disabled
    """
    if aiohttp_openmetrics is None:
        raise HTTPNotFound
    return await aiohttp_openmetrics.metrics(request)


def metrics_handler() -> Middleware:
    """
    middleware for metrics support

    Returns:
        Middleware: middleware function to handle server metrics
    """
    if aiohttp_openmetrics is not None:
        return aiohttp_openmetrics.metrics_middleware

    @middleware
    async def handle(request: Request, handler: HandlerType) -> StreamResponse:
        return await handler(request)

    return handle
