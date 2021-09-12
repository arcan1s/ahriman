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
from aiohttp.web import HTTPFound, HTTPUnauthorized, Response

from ahriman.core.auth.helpers import remember
from ahriman.web.views.base import BaseView


class LoginView(BaseView):
    """
    login endpoint view
    """

    async def post(self) -> Response:
        """
        login user to service

        either JSON body or form data must be supplied the following fields are required:
        {
            "username": "username"  # username to use for login
            "password": "pa55w0rd"  # password to use for login
        }

        :return: redirect to main page
        """
        data = await self.extract_data()
        username = data.get("username")

        response = HTTPFound("/")
        if await self.validator.check_credentials(username, data.get("password")):
            await remember(self.request, response, username)
            return response

        raise HTTPUnauthorized()
