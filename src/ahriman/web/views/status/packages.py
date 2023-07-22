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
import aiohttp_apispec  # type: ignore[import]

from aiohttp.web import HTTPNoContent, Response, json_response

from ahriman.models.user_access import UserAccess
from ahriman.web.schemas import AuthSchema, ErrorSchema, PackageStatusSchema
from ahriman.web.views.base import BaseView


class PackagesView(BaseView):
    """
    global watcher view

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    GET_PERMISSION = UserAccess.Read
    POST_PERMISSION = UserAccess.Full

    @aiohttp_apispec.docs(
        tags=["Packages"],
        summary="Get packages list",
        description="Retrieve all packages and their descriptors",
        responses={
            200: {"description": "Success response", "schema": PackageStatusSchema(many=True)},
            401: {"description": "Authorization required", "schema": ErrorSchema},
            403: {"description": "Access is forbidden", "schema": ErrorSchema},
            500: {"description": "Internal server error", "schema": ErrorSchema},
        },
        security=[{"token": [GET_PERMISSION]}],
    )
    @aiohttp_apispec.cookies_schema(AuthSchema)
    async def get(self) -> Response:
        """
        get current packages status

        Returns:
            Response: 200 with package description on success
        """
        response = [
            {
                "package": package.view(),
                "status": status.view()
            } for package, status in self.service.packages
        ]
        return json_response(response)

    @aiohttp_apispec.docs(
        tags=["Packages"],
        summary="Load packages",
        description="Load packages from cache",
        responses={
            204: {"description": "Success response"},
            401: {"description": "Authorization required", "schema": ErrorSchema},
            403: {"description": "Access is forbidden", "schema": ErrorSchema},
            500: {"description": "Internal server error", "schema": ErrorSchema},
        },
        security=[{"token": [POST_PERMISSION]}],
    )
    @aiohttp_apispec.cookies_schema(AuthSchema)
    async def post(self) -> None:
        """
        reload all packages from repository

        Raises:
            HTTPNoContent: on success response
        """
        self.service.load()

        raise HTTPNoContent()
