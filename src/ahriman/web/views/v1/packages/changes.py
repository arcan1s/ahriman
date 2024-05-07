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

from aiohttp.web import HTTPBadRequest, HTTPNoContent, HTTPNotFound, Response, json_response

from ahriman.core.exceptions import UnknownPackageError
from ahriman.models.changes import Changes
from ahriman.models.user_access import UserAccess
from ahriman.web.schemas import AuthSchema, ChangesSchema, ErrorSchema, PackageNameSchema, RepositoryIdSchema
from ahriman.web.views.base import BaseView
from ahriman.web.views.status_view_guard import StatusViewGuard


class ChangesView(StatusViewGuard, BaseView):
    """
    package changes web view

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    GET_PERMISSION = UserAccess.Reporter
    POST_PERMISSION = UserAccess.Full
    ROUTES = ["/api/v1/packages/{package}/changes"]

    @aiohttp_apispec.docs(
        tags=["Packages"],
        summary="Get package changes",
        description="Retrieve package changes since the last build",
        responses={
            200: {"description": "Success response", "schema": ChangesSchema},
            401: {"description": "Authorization required", "schema": ErrorSchema},
            403: {"description": "Access is forbidden", "schema": ErrorSchema},
            404: {"description": "Package base and/or repository are unknown", "schema": ErrorSchema},
            500: {"description": "Internal server error", "schema": ErrorSchema},
        },
        security=[{"token": [GET_PERMISSION]}],
    )
    @aiohttp_apispec.cookies_schema(AuthSchema)
    @aiohttp_apispec.match_info_schema(PackageNameSchema)
    @aiohttp_apispec.querystring_schema(RepositoryIdSchema)
    async def get(self) -> Response:
        """
        get package changes

        Returns:
            Response: 200 with package change on success

        Raises:
            HTTPNotFound: if package base is unknown
        """
        package_base = self.request.match_info["package"]

        try:
            changes = self.service().package_changes_get(package_base)
        except UnknownPackageError:
            raise HTTPNotFound(reason=f"Package {package_base} is unknown")

        return json_response(changes.view())

    @aiohttp_apispec.docs(
        tags=["Packages"],
        summary="Update package changes",
        description="Update package changes to the new ones",
        responses={
            204: {"description": "Success response"},
            400: {"description": "Bad data is supplied", "schema": ErrorSchema},
            401: {"description": "Authorization required", "schema": ErrorSchema},
            403: {"description": "Access is forbidden", "schema": ErrorSchema},
            404: {"description": "Package base and/or repository are unknown", "schema": ErrorSchema},
            500: {"description": "Internal server error", "schema": ErrorSchema},
        },
        security=[{"token": [POST_PERMISSION]}],
    )
    @aiohttp_apispec.cookies_schema(AuthSchema)
    @aiohttp_apispec.match_info_schema(PackageNameSchema)
    @aiohttp_apispec.querystring_schema(RepositoryIdSchema)
    @aiohttp_apispec.json_schema(ChangesSchema)
    async def post(self) -> None:
        """
        insert new package changes

        Raises:
            HTTPBadRequest: if bad data is supplied
            HTTPNoContent: in case of success response
        """
        package_base = self.request.match_info["package"]

        try:
            data = await self.request.json()
            last_commit_sha = data.get("last_commit_sha")  # empty/null meant removal
            change = data.get("changes")
        except Exception as ex:
            raise HTTPBadRequest(reason=str(ex))

        changes = Changes(last_commit_sha, change)
        try:
            self.service().package_changes_update(package_base, changes)
        except UnknownPackageError:
            raise HTTPNotFound(reason=f"Package {package_base} is unknown")

        raise HTTPNoContent
