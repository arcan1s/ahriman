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
from aiohttp.web import HTTPBadRequest, Response, json_response

from ahriman.models.user_access import UserAccess
from ahriman.web.apispec.decorators import apidocs
from ahriman.web.schemas import PackageNamesSchema, ProcessIdSchema, RepositoryIdSchema
from ahriman.web.views.base import BaseView


class RemoveView(BaseView):
    """
    remove package web view

    Attributes:
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    POST_PERMISSION = UserAccess.Full
    ROUTES = ["/api/v1/service/remove"]

    @apidocs(
        tags=["Actions"],
        summary="Remove packages",
        description="Remove specified packages from the repository",
        permission=POST_PERMISSION,
        error_400_enabled=True,
        error_404_description="Repository is unknown",
        schema=ProcessIdSchema,
        query_schema=RepositoryIdSchema,
        body_schema=PackageNamesSchema,
    )
    async def post(self) -> Response:
        """
        remove existing packages

        Returns:
            Response: 200 with spawned process id

        Raises:
            HTTPBadRequest: if bad data is supplied
        """
        try:
            data = await self.request.json()
            packages = self.get_non_empty(lambda key: [package for package in data[key] if package], "packages")
        except Exception as ex:
            raise HTTPBadRequest(reason=str(ex))

        repository_id = self.repository_id()
        process_id = self.spawner.packages_remove(repository_id, packages)

        return json_response({"process_id": process_id})
