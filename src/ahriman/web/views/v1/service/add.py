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

from aiohttp.web import HTTPBadRequest, Response, json_response

from ahriman.models.pkgbuild_patch import PkgbuildPatch
from ahriman.models.user_access import UserAccess
from ahriman.web.schemas import AuthSchema, ErrorSchema, PackagePatchSchema, ProcessIdSchema, RepositoryIdSchema
from ahriman.web.views.base import BaseView


class AddView(BaseView):
    """
    add package web view

    Attributes:
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    POST_PERMISSION = UserAccess.Full
    ROUTES = ["/api/v1/service/add"]

    @aiohttp_apispec.docs(
        tags=["Actions"],
        summary="Add new package",
        description="Add new package(s) from AUR",
        responses={
            200: {"description": "Success response", "schema": ProcessIdSchema},
            400: {"description": "Bad data is supplied", "schema": ErrorSchema},
            401: {"description": "Authorization required", "schema": ErrorSchema},
            403: {"description": "Access is forbidden", "schema": ErrorSchema},
            404: {"description": "Repository is unknown", "schema": ErrorSchema},
            500: {"description": "Internal server error", "schema": ErrorSchema},
        },
        security=[{"token": [POST_PERMISSION]}],
    )
    @aiohttp_apispec.cookies_schema(AuthSchema)
    @aiohttp_apispec.querystring_schema(RepositoryIdSchema)
    @aiohttp_apispec.json_schema(PackagePatchSchema)
    async def post(self) -> Response:
        """
        add new package

        Returns:
            Response: 200 with spawned process id

        Raises:
            HTTPBadRequest: if bad data is supplied
        """
        try:
            data = await self.request.json()
            packages = self.get_non_empty(lambda key: [package for package in data[key] if package], "packages")
            patches = [PkgbuildPatch.parse(patch["key"], patch.get("value", "")) for patch in data.get("patches", [])]
        except Exception as ex:
            raise HTTPBadRequest(reason=str(ex))

        repository_id = self.repository_id()
        username = await self.username()
        process_id = self.spawner.packages_add(
            repository_id,
            packages,
            username,
            patches=patches,
            now=True,
            increment=data.get("increment", True),
            refresh=data.get("refresh", False),
        )

        return json_response({"process_id": process_id})
