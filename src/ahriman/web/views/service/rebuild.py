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
from aiohttp.web import HTTPBadRequest, HTTPNoContent

from ahriman.models.user_access import UserAccess
from ahriman.web.views.base import BaseView


class RebuildView(BaseView):
    """
    rebuild packages web view

    Attributes:
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    POST_PERMISSION = UserAccess.Full

    async def post(self) -> None:
        """
        rebuild packages based on their dependency

        JSON body must be supplied, the following model is used::

            {
                "packages": ["ahriman"]  # either list of packages or package name of dependency
            }

        Raises:
            HTTPBadRequest: if bad data is supplied
            HTTPNoContent: in case of success response

        Examples:
            Example of command by using curl::

                $ curl -v -H 'Content-Type: application/json' 'http://example.com/api/v1/service/rebuild' -d '{"packages": ["python"]}'
                > POST /api/v1/service/rebuild HTTP/1.1
                > Host: example.com
                > User-Agent: curl/7.86.0
                > Accept: */*
                > Content-Type: application/json
                > Content-Length: 24
                >
                < HTTP/1.1 204 No Content
                < Date: Sun, 27 Nov 2022 00:22:26 GMT
                < Server: Python/3.10 aiohttp/3.8.3
                <
        """
        try:
            data = await self.extract_data(["packages"])
            packages = self.get_non_empty(lambda key: [package for package in data[key] if package], "packages")
            depends_on = next(package for package in packages)
        except Exception as e:
            raise HTTPBadRequest(reason=str(e))

        self.spawner.packages_rebuild(depends_on)

        raise HTTPNoContent()
