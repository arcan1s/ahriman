#
# Copyright (c) 2021-2022 ahriman team.
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
from aiohttp.web import HTTPNotFound, Response, json_response
from typing import Callable, List

from ahriman.core.alpm.remote.aur import AUR
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

    GET_PERMISSION = HEAD_PERMISSION = UserAccess.Read

    async def get(self) -> Response:
        """
        search packages in AUR

        search string (non empty) must be supplied as ``for`` parameter

        Returns:
            Response: 200 with found package bases and descriptions sorted by base

        Raises:
            HTTPNotFound: if no packages found
        """
        search: List[str] = self.request.query.getall("for", default=[])
        packages = AUR.multisearch(*search, pacman=self.service.repository.pacman)
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
