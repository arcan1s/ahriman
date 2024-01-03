#
# Copyright (c) 2021-2024 ahriman team.
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
import aiohttp_apispec  # type: ignore[import-untyped]

from aiohttp.web import Response, json_response

from ahriman import __version__
from ahriman.models.user_access import UserAccess
from ahriman.web.schemas import AuthSchema, ErrorSchema, InfoSchema
from ahriman.web.views.base import BaseView


class InfoView(BaseView):
    """
    web service information view

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
    """

    GET_PERMISSION = UserAccess.Unauthorized
    ROUTES = ["/api/v1/info"]

    @aiohttp_apispec.docs(
        tags=["Status"],
        summary="Service information",
        description="Perform basic service health check and returns its information",
        responses={
            200: {"description": "Success response", "schema": InfoSchema},
            401: {"description": "Authorization required", "schema": ErrorSchema},
            403: {"description": "Access is forbidden", "schema": ErrorSchema},
            500: {"description": "Internal server error", "schema": ErrorSchema},
        },
        security=[{"token": [GET_PERMISSION]}],
    )
    @aiohttp_apispec.cookies_schema(AuthSchema)
    async def get(self) -> Response:
        """
        get service information

        Returns:
            Response: 200 with service information object
        """
        response = {
            "auth": self.validator.enabled,
            "repositories": [
                repository_id.view()
                for repository_id in sorted(self.services)
            ],
            "version": __version__,
        }

        return json_response(response)
