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
from aiohttp.web import HTTPNoContent

from ahriman.models.user_access import UserAccess
from ahriman.web.views.base import BaseView


class UpdateView(BaseView):
    """
    update repository web view

    Attributes:
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    POST_PERMISSION = UserAccess.Full

    async def post(self) -> None:
        """
        run repository update. No parameters supported here

        Raises:
            HTTPNoContent: in case of success response

        Examples:
            Example of command by using curl::

                $ curl -v -XPOST 'http://example.com/api/v1/service/update'
                > POST /api/v1/service/update HTTP/1.1
                > Host: example.com
                > User-Agent: curl/7.86.0
                > Accept: */*
                >
                < HTTP/1.1 204 No Content
                < Date: Fri, 25 Nov 2022 22:57:56 GMT
                < Server: Python/3.10 aiohttp/3.8.3
                <
        """
        self.spawner.packages_update()

        raise HTTPNoContent()
