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
import itertools

from aiohttp.web import HTTPNoContent, Response, json_response
from collections.abc import Callable

from ahriman.models.build_status import BuildStatus
from ahriman.models.package import Package
from ahriman.models.user_access import UserAccess
from ahriman.web.apispec.decorators import apidocs
from ahriman.web.schemas import PackageStatusSchema, PaginationSchema, RepositoryIdSchema
from ahriman.web.views.base import BaseView
from ahriman.web.views.status_view_guard import StatusViewGuard


class PackagesView(StatusViewGuard, BaseView):
    """
    global watcher view

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    GET_PERMISSION = UserAccess.Read
    POST_PERMISSION = UserAccess.Full
    ROUTES = ["/api/v1/packages"]

    @apidocs(
        tags=["packages"],
        summary="Get packages list",
        description="Retrieve packages and their descriptors",
        permission=GET_PERMISSION,
        error_400_enabled=True,
        error_404_description="Repository is unknown",
        schema=PackageStatusSchema(many=True),
        query_schema=PaginationSchema,
    )
    async def get(self) -> Response:
        """
        get current packages status

        Returns:
            Response: 200 with package description on success
        """
        limit, offset = self.page()
        stop = offset + limit if limit >= 0 else None

        repository_id = self.repository_id()
        packages = self.service(repository_id).packages

        comparator: Callable[[tuple[Package, BuildStatus]], str] = lambda items: items[0].base
        response = [
            {
                "package": package.view(),
                "status": status.view(),
                "repository": repository_id.view(),
            } for package, status in itertools.islice(sorted(packages, key=comparator), offset, stop)
        ]

        return json_response(response)

    @apidocs(
        tags=["Packages"],
        summary="Load packages",
        description="Load packages from cache",
        permission=POST_PERMISSION,
        error_404_description="Repository is unknown",
        query_schema=RepositoryIdSchema,
    )
    async def post(self) -> None:
        """
        reload all packages from repository

        Raises:
            HTTPNoContent: on success response
        """
        self.service().load()

        raise HTTPNoContent
