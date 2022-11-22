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
import aiohttp_jinja2
import logging

from aiohttp.web import middleware, Request
from aiohttp.web_exceptions import HTTPClientError, HTTPException, HTTPServerError, HTTPUnauthorized
from aiohttp.web_response import json_response, StreamResponse

from ahriman.web.middlewares import HandlerType, MiddlewareType


__all__ = ["exception_handler"]


def exception_handler(logger: logging.Logger) -> MiddlewareType:
    """
    exception handler middleware. Just log any exception (except for client ones)

    Args:
        logger(logging.Logger): class logger

    Returns:
        MiddlewareType: built middleware
    """
    @middleware
    async def handle(request: Request, handler: HandlerType) -> StreamResponse:
        try:
            return await handler(request)
        except HTTPUnauthorized as e:
            if is_templated_unauthorized(request):
                context = {"code": e.status_code, "reason": e.reason}
                return aiohttp_jinja2.render_template("error.jinja2", request, context, status=e.status_code)
            return json_response(data={"error": e.reason}, status=e.status_code)
        except HTTPClientError as e:
            return json_response(data={"error": e.reason}, status=e.status_code)
        except HTTPServerError as e:
            logger.exception("server exception during performing request to %s", request.path)
            return json_response(data={"error": e.reason}, status=e.status_code)
        except HTTPException:  # just raise 2xx and 3xx codes
            raise
        except Exception as e:
            logger.exception("unknown exception during performing request to %s", request.path)
            return json_response(data={"error": str(e)}, status=500)

    return handle


def is_templated_unauthorized(request: Request) -> bool:
    """
    check if the request is eligible for rendering html template

    Args:
        request(Request): source request to check

    Returns:
        bool: True in case if response should be rendered as html and False otherwise
    """
    return request.path in ("/api/v1/login", "/api/v1/logout") \
        and "application/json" not in request.headers.getall("accept", [])
