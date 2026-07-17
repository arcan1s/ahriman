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
from aiohttp.web import HTTPFound, HTTPNotFound
from typing import ClassVar

from ahriman.models.user_access import UserAccess
from ahriman.web.views.base import BaseView


class StaticView(BaseView):
    """
    special workaround for static files redirection (e.g. favicon)

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
    """

    GET_PERMISSION: ClassVar[UserAccess] = UserAccess.Unauthorized
    ROUTES = ["/favicon.ico"]

    async def get(self) -> None:
        """
        process get request. No parameters supported here

        Raises:
            HTTPFound: on success response
            HTTPNotFound: if path is invalid or unknown
        """
        if self.request.path in self.ROUTES:  # explicit validation
            raise HTTPFound(f"/static{self.request.path}")
        raise HTTPNotFound
