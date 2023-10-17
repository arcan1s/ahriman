#
# Copyright (c) 2021-2023 ahriman team.
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

from ahriman.models.user_access import UserAccess
from ahriman.web.schemas import AuthSchema, ErrorSchema, RepositoryIdSchema
from ahriman.web.views.base import BaseView


class RepositoriesView(BaseView):
    """
    repositories view

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
    """

    GET_PERMISSION = UserAccess.Read
    ROUTES = ["/api/v1/repositories"]

    @aiohttp_apispec.docs(
        tags=["Status"],
        summary="Available repositories",
        description="List available repositories",
        responses={
            200: {"description": "Success response", "schema": RepositoryIdSchema(many=True)},
            401: {"description": "Authorization required", "schema": ErrorSchema},
            403: {"description": "Access is forbidden", "schema": ErrorSchema},
            500: {"description": "Internal server error", "schema": ErrorSchema},
        },
        security=[{"token": [GET_PERMISSION]}],
    )
    @aiohttp_apispec.cookies_schema(AuthSchema)
    async def get(self) -> Response:
        """
        get list of available repositories

        Returns:
            Response: 200 with service status object
        """
        repositories = [
            repository_id.view()
            for repository_id in sorted(self.services)
        ]

        return json_response(repositories)
