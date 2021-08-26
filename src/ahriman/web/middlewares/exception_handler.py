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
from aiohttp.web import middleware, Request
from aiohttp.web_exceptions import HTTPClientError
from aiohttp.web_response import StreamResponse
from logging import Logger

from ahriman.web.middlewares import HandlerType, MiddlewareType


def exception_handler(logger: Logger) -> MiddlewareType:
    """
    exception handler middleware. Just log any exception (except for client ones)
    :param logger: class logger
    :return: built middleware
    """
    @middleware
    async def handle(request: Request, handler: HandlerType) -> StreamResponse:
        try:
            return await handler(request)
        except HTTPClientError:
            raise
        except Exception:
            logger.exception("exception during performing request to %s", request.path)
            raise

    return handle
