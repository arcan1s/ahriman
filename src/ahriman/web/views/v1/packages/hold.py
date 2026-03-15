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
from aiohttp.web import HTTPBadRequest, HTTPNoContent, HTTPNotFound
from typing import ClassVar

from ahriman.core.exceptions import UnknownPackageError
from ahriman.models.user_access import UserAccess
from ahriman.web.apispec.decorators import apidocs
from ahriman.web.schemas import HoldSchema, PackageNameSchema, RepositoryIdSchema
from ahriman.web.views.base import BaseView
from ahriman.web.views.status_view_guard import StatusViewGuard


class HoldView(StatusViewGuard, BaseView):
    """
    package hold web view

    Attributes:
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    POST_PERMISSION: ClassVar[UserAccess] = UserAccess.Full
    ROUTES = ["/api/v1/packages/{package}/hold"]

    @apidocs(
        tags=["Packages"],
        summary="Update package hold status",
        description="Set package hold status",
        permission=POST_PERMISSION,
        error_400_enabled=True,
        error_404_description="Package base and/or repository are unknown",
        match_schema=PackageNameSchema,
        query_schema=RepositoryIdSchema,
        body_schema=HoldSchema,
    )
    async def post(self) -> None:
        """
        update package hold status

        Raises:
            HTTPBadRequest: if bad data is supplied
            HTTPNoContent: in case of success response
            HTTPNotFound: if no package was found
        """
        package_base = self.request.match_info["package"]

        try:
            data = await self.request.json()
            is_held = data["is_held"]
        except Exception as ex:
            raise HTTPBadRequest(reason=str(ex))

        try:
            self.service().package_hold_update(package_base, enabled=is_held)
        except UnknownPackageError:
            raise HTTPNotFound(reason=f"Package {package_base} is unknown")

        raise HTTPNoContent
