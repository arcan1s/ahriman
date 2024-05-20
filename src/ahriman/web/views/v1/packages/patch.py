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

from aiohttp.web import HTTPNoContent, HTTPNotFound, Response, json_response

from ahriman.models.user_access import UserAccess
from ahriman.web.schemas import AuthSchema, ErrorSchema, PatchNameSchema, PatchSchema
from ahriman.web.views.base import BaseView
from ahriman.web.views.status_view_guard import StatusViewGuard


class PatchView(StatusViewGuard, BaseView):
    """
    package patch web view

    Attributes:
        DELETE_PERMISSION(UserAccess): (class attribute) delete permissions of self
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
    """

    DELETE_PERMISSION = UserAccess.Full
    GET_PERMISSION = UserAccess.Reporter
    ROUTES = ["/api/v1/packages/{package}/patches/{patch}"]

    @aiohttp_apispec.docs(
        tags=["Packages"],
        summary="Delete package patch",
        description="Delete package patch by variable",
        responses={
            204: {"description": "Success response"},
            401: {"description": "Authorization required", "schema": ErrorSchema},
            403: {"description": "Access is forbidden", "schema": ErrorSchema},
            500: {"description": "Internal server error", "schema": ErrorSchema},
        },
        security=[{"token": [DELETE_PERMISSION]}],
    )
    @aiohttp_apispec.cookies_schema(AuthSchema)
    @aiohttp_apispec.match_info_schema(PatchNameSchema)
    async def delete(self) -> None:
        """
        delete package patch

        Raises:
            HTTPNoContent: on success response
        """
        package_base = self.request.match_info["package"]
        variable = self.request.match_info["patch"]

        self.service().package_patches_remove(package_base, variable)

        raise HTTPNoContent

    @aiohttp_apispec.docs(
        tags=["Packages"],
        summary="Get package patch",
        description="Retrieve package patch by variable",
        responses={
            200: {"description": "Success response", "schema": PatchSchema},
            401: {"description": "Authorization required", "schema": ErrorSchema},
            403: {"description": "Access is forbidden", "schema": ErrorSchema},
            404: {"description": "Patch name is unknown", "schema": ErrorSchema},
            500: {"description": "Internal server error", "schema": ErrorSchema},
        },
        security=[{"token": [GET_PERMISSION]}],
    )
    @aiohttp_apispec.cookies_schema(AuthSchema)
    @aiohttp_apispec.match_info_schema(PatchNameSchema)
    async def get(self) -> Response:
        """
        get package patch

        Returns:
            Response: 200 with package patch on success

        Raises:
            HTTPNotFound: if package patch is unknown
        """
        package_base = self.request.match_info["package"]
        variable = self.request.match_info["patch"]

        patches = self.service().package_patches_get(package_base, variable)

        selected = next((patch for patch in patches if patch.key == variable), None)
        if selected is None:
            raise HTTPNotFound(reason=f"Patch {variable} is unknown")

        return json_response(selected.view())
