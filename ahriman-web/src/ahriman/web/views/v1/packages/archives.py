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
from aiohttp.web import Response
from typing import ClassVar

from ahriman.models.user_access import UserAccess
from ahriman.web.apispec.decorators import apidocs
from ahriman.web.schemas import PackageNameSchema, PackageSchema, RepositoryIdSchema
from ahriman.web.views.base import BaseView
from ahriman.web.views.status_view_guard import StatusViewGuard


class Archives(StatusViewGuard, BaseView):
    """
    package archives web view

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
    """

    GET_PERMISSION: ClassVar[UserAccess] = UserAccess.Reporter
    ROUTES = ["/api/v1/packages/{package}/archives"]

    @apidocs(
        tags=["Packages"],
        summary="Get package archives",
        description="Retrieve built package archives for the base",
        permission=GET_PERMISSION,
        error_404_description="Package base and/or repository are unknown",
        schema=PackageSchema(many=True),
        match_schema=PackageNameSchema,
        query_schema=RepositoryIdSchema,
    )
    async def get(self) -> Response:
        """
        get package archives

        Returns:
            Response: 200 with package archives on success

        Raises:
            HTTPNotFound: if no package was found
        """
        package_base = self.request.match_info["package"]

        archives = await self.service(package_base=package_base).package_archives(package_base)

        return self.json_response([archive.view() for archive in archives])
