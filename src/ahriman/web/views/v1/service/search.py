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
import aiohttp_apispec  # type: ignore[import-untyped]

from aiohttp.web import HTTPBadRequest, HTTPNotFound, Response, json_response
from collections.abc import Callable

from ahriman.core.alpm.remote import AUR
from ahriman.models.aur_package import AURPackage
from ahriman.models.user_access import UserAccess
from ahriman.web.schemas import AURPackageSchema, AuthSchema, ErrorSchema, SearchSchema
from ahriman.web.views.base import BaseView


class SearchView(BaseView):
    """
    AUR search web view

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
    """

    GET_PERMISSION = UserAccess.Reporter
    ROUTES = ["/api/v1/service/search"]

    @aiohttp_apispec.docs(
        tags=["Actions"],
        summary="Search for package",
        description="Search for package in AUR",
        responses={
            200: {"description": "Success response", "schema": AURPackageSchema(many=True)},
            400: {"description": "Bad data is supplied", "schema": ErrorSchema},
            401: {"description": "Authorization required", "schema": ErrorSchema},
            403: {"description": "Access is forbidden", "schema": ErrorSchema},
            404: {"description": "Package base is unknown", "schema": ErrorSchema},
            500: {"description": "Internal server error", "schema": ErrorSchema},
        },
        security=[{"token": [GET_PERMISSION]}],
    )
    @aiohttp_apispec.cookies_schema(AuthSchema)
    @aiohttp_apispec.querystring_schema(SearchSchema)
    async def get(self) -> Response:
        """
        search packages in AUR

        Returns:
            Response: 200 with found package bases and descriptions sorted by base

        Raises:
            HTTPBadRequest: in case if bad data is supplied
            HTTPNotFound: if no packages found
        """
        try:
            search: list[str] = self.get_non_empty(lambda key: self.request.query.getall(key, default=[]), "for")
            packages = AUR.multisearch(*search, pacman=self.service.repository.pacman)
        except Exception as ex:
            raise HTTPBadRequest(reason=str(ex))

        if not packages:
            raise HTTPNotFound(reason=f"No packages found for terms: {search}")

        comparator: Callable[[AURPackage], str] = lambda item: str(item.package_base)
        response = [
            {
                "package": package.package_base,
                "description": package.description,
            } for package in sorted(packages, key=comparator)
        ]
        return json_response(response)
