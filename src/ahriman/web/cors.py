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
import aiohttp_cors

from aiohttp.web import Application


__all__ = ["setup_cors"]


def setup_cors(application: Application) -> aiohttp_cors.CorsConfig:
    """
    setup CORS for the web application

    Args:
        application(Application): web application instance

    Returns:
        aiohttp_cors.CorsConfig: generated CORS configuration
    """
    cors = aiohttp_cors.setup(application, defaults={
        "*": aiohttp_cors.ResourceOptions(  # type: ignore[no-untyped-call]
            expose_headers="*",
            allow_headers="*",
            allow_methods="*",
        )
    })
    for route in application.router.routes():
        cors.add(route)

    return cors
