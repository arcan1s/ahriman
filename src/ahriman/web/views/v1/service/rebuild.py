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

from aiohttp.web import HTTPBadRequest, Response, json_response

from ahriman.models.user_access import UserAccess
from ahriman.web.schemas import AuthSchema, ErrorSchema, PackageNamesSchema, ProcessIdSchema
from ahriman.web.views.base import BaseView


class RebuildView(BaseView):
    """
    rebuild packages web view

    Attributes:
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    POST_PERMISSION = UserAccess.Full
    ROUTES = ["/api/v1/service/rebuild"]

    @aiohttp_apispec.docs(
        tags=["Actions"],
        summary="Rebuild packages",
        description="Rebuild packages which depend on specified one",
        responses={
            200: {"description": "Success response", "schema": ProcessIdSchema},
            400: {"description": "Bad data is supplied", "schema": ErrorSchema},
            401: {"description": "Authorization required", "schema": ErrorSchema},
            403: {"description": "Access is forbidden", "schema": ErrorSchema},
            500: {"description": "Internal server error", "schema": ErrorSchema},
        },
        security=[{"token": [POST_PERMISSION]}],
    )
    @aiohttp_apispec.cookies_schema(AuthSchema)
    @aiohttp_apispec.json_schema(PackageNamesSchema)
    async def post(self) -> Response:
        """
        rebuild packages based on their dependency

        Returns:
            Response: 200 with spawned process id

        Raises:
            HTTPBadRequest: if bad data is supplied
        """
        try:
            data = await self.extract_data(["packages"])
            packages = self.get_non_empty(lambda key: [package for package in data[key] if package], "packages")
            depends_on = next(iter(packages))
        except Exception as ex:
            raise HTTPBadRequest(reason=str(ex))

        username = await self.username()
        process_id = self.spawner.packages_rebuild(depends_on, username)

        return json_response({"process_id": process_id})
