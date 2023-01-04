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
from aiohttp.web import HTTPBadRequest, HTTPNotFound, Response, json_response
from typing import Callable, List

from ahriman.core.alpm.remote import AUR
from ahriman.models.aur_package import AURPackage
from ahriman.models.user_access import UserAccess
from ahriman.web.views.base import BaseView


class SearchView(BaseView):
    """
    AUR search web view

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
        HEAD_PERMISSION(UserAccess): (class attribute) head permissions of self
    """

    GET_PERMISSION = HEAD_PERMISSION = UserAccess.Reporter

    async def get(self) -> Response:
        """
        search packages in AUR. Search string (non-empty) must be supplied as ``for`` parameter

        Returns:
            Response: 200 with found package bases and descriptions sorted by base

        Raises:
            HTTPBadRequest: in case if bad data is supplied
            HTTPNotFound: if no packages found

        Examples:
            Example of command by using curl::

                $ curl -v -H 'Accept: application/json' 'http://example.com/api/v1/service/search?for=ahriman'
                > GET /api/v1/service/search?for=ahriman HTTP/1.1
                > Host: example.com
                > User-Agent: curl/7.86.0
                > Accept: application/json
                >
                < HTTP/1.1 200 OK
                < Content-Type: application/json; charset=utf-8
                < Content-Length: 148
                < Date: Wed, 23 Nov 2022 19:07:13 GMT
                < Server: Python/3.10 aiohttp/3.8.3
                <
                [{"package": "ahriman", "description": "ArcH linux ReposItory MANager"}, {"package": "ahriman-git", "description": "ArcH Linux ReposItory MANager"}]
        """
        try:
            search: List[str] = self.get_non_empty(lambda key: self.request.query.getall(key, default=[]), "for")
            packages = AUR.multisearch(*search, pacman=self.service.repository.pacman)
        except Exception as e:
            raise HTTPBadRequest(reason=str(e))

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
