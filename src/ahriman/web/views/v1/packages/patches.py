#
# Copyright (c) 2021-2025 ahriman team.
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
from aiohttp.web import HTTPBadRequest, HTTPNoContent, Response, json_response

from ahriman.models.pkgbuild_patch import PkgbuildPatch
from ahriman.models.user_access import UserAccess
from ahriman.web.apispec.decorators import apidocs
from ahriman.web.schemas import PackageNameSchema, PatchSchema
from ahriman.web.views.base import BaseView
from ahriman.web.views.status_view_guard import StatusViewGuard


class PatchesView(StatusViewGuard, BaseView):
    """
    package patches web view

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    GET_PERMISSION = UserAccess.Reporter
    POST_PERMISSION = UserAccess.Full
    ROUTES = ["/api/v1/packages/{package}/patches"]

    @apidocs(
        tags=["Packages"],
        summary="Get package patches",
        description="Retrieve all package patches",
        permission=GET_PERMISSION,
        schema=PatchSchema(many=True),
        match_schema=PackageNameSchema,
    )
    async def get(self) -> Response:
        """
        get package patches

        Returns:
            Response: 200 with package patches on success
        """
        package_base = self.request.match_info["package"]
        patches = self.service().package_patches_get(package_base, None)

        response = [patch.view() for patch in patches]
        return json_response(response)

    @apidocs(
        tags=["Packages"],
        summary="Update package patch",
        description="Update or create package patch",
        permission=POST_PERMISSION,
        error_400_enabled=True,
        match_schema=PackageNameSchema,
        body_schema=PatchSchema,
    )
    async def post(self) -> None:
        """
        update or create package patch

        Raises:
            HTTPBadRequest: if bad data is supplied
            HTTPNoContent: on success response
        """
        package_base = self.request.match_info["package"]

        try:
            data = await self.request.json()
            key = data.get("key")
            value = data["value"]
        except Exception as ex:
            raise HTTPBadRequest(reason=str(ex))

        self.service().package_patches_update(package_base, PkgbuildPatch.parse(key, value))

        raise HTTPNoContent
