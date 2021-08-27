#
# Copyright (c) 2021 ahriman team.
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
import aiohttp_security  # type: ignore

from aiohttp.web import HTTPFound, Response

from ahriman.web.views.base import BaseView


class LogoutView(BaseView):
    """
    logout endpoint view
    """

    async def post(self) -> Response:
        """
        logout user from the service. No parameters supported here
        :return: redirect to main page
        """
        await aiohttp_security.check_authorized(self.request)

        response = HTTPFound("/")
        await aiohttp_security.forget(self.request, response)

        return response
