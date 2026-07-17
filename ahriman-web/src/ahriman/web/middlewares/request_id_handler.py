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
import uuid

from aiohttp.typedefs import Middleware
from aiohttp.web import Request, StreamResponse, middleware

from ahriman.core.log.log_context import LogContext
from ahriman.web.middlewares import HandlerType


__all__ = ["request_id_handler"]


def request_id_handler() -> Middleware:
    """
    middleware to trace request id header

    Returns:
        Middleware: request id processing middleware
    """
    @middleware
    async def handle(request: Request, handler: HandlerType) -> StreamResponse:
        request_id = request.headers.getone("X-Request-ID", str(uuid.uuid4()))

        token = LogContext.set("request_id", request_id)
        try:
            response = await handler(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            LogContext.reset("request_id", token)

    return handle
