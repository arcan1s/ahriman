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
import hashlib

from aiohttp import ETag
from aiohttp.typedefs import Middleware
from aiohttp.web import HTTPNotModified, Request, Response, StreamResponse, middleware

from ahriman.web.middlewares import HandlerType


__all__ = ["etag_handler"]


def etag_handler() -> Middleware:
    """
    middleware to handle ETag header for conditional requests. It computes ETag from the response body
    and returns 304 Not Modified if the client sends a matching ``If-None-Match`` header

    Returns:
        Middleware: built middleware

    Raises:
        HTTPNotModified: if content matches ``If-None-Match`` header sent
    """
    @middleware
    async def handle(request: Request, handler: HandlerType) -> StreamResponse:
        response = await handler(request)

        if not isinstance(response, Response) or not isinstance(response.body, bytes):
            return response

        if request.method not in ("GET", "HEAD"):
            return response

        etag = ETag(value=hashlib.md5(response.body, usedforsecurity=False).hexdigest())
        response.etag = etag

        if request.if_none_match is not None and etag in request.if_none_match:
            raise HTTPNotModified(headers={"ETag": response.headers["ETag"]})

        return response

    return handle
