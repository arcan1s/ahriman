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
from aiohttp.web import HTTPNoContent, Response, json_response

from ahriman.models.user_access import UserAccess
from ahriman.web.views.base import BaseView


class PackagesView(BaseView):
    """
    global watcher view

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
        HEAD_PERMISSION(UserAccess): (class attribute) head permissions of self
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    GET_PERMISSION = HEAD_PERMISSION = UserAccess.Read
    POST_PERMISSION = UserAccess.Full

    async def get(self) -> Response:
        """
        get current packages status

        Returns:
            Response: 200 with package description on success

        Examples:
            Example of command by using curl::

                $ curl -v -H 'Accept: application/json' 'http://example.com/api/v1/packages'
                > GET /api/v1/packages HTTP/1.1
                > Host: example.com
                > User-Agent: curl/7.86.0
                > Accept: application/json
                >
                < HTTP/1.1 200 OK
                < Content-Type: application/json; charset=utf-8
                < Content-Length: 2687
                < Date: Wed, 23 Nov 2022 19:35:24 GMT
                < Server: Python/3.10 aiohttp/3.8.3
                <
                [{"package": {"base": "ahriman", "version": "2.3.0-1", "remote": {"git_url": "https://aur.archlinux.org/ahriman.git", "web_url": "https://aur.archlinux.org/packages/ahriman", "path": ".", "branch": "master", "source": "aur"}, "packages": {"ahriman": {"architecture": "any", "archive_size": 247573, "build_date": 1669231069, "depends": ["devtools", "git", "pyalpm", "python-inflection", "python-passlib", "python-requests", "python-setuptools", "python-srcinfo"], "description": "ArcH linux ReposItory MANager", "filename": "ahriman-2.3.0-1-any.pkg.tar.zst", "groups": [], "installed_size": 1676153, "licenses": ["GPL3"], "provides": [], "url": "https://github.com/arcan1s/ahriman"}}}, "status": {"status": "success", "timestamp": 1669231136}}]
        """
        response = [
            {
                "package": package.view(),
                "status": status.view()
            } for package, status in self.service.packages
        ]
        return json_response(response)

    async def post(self) -> None:
        """
        reload all packages from repository. No parameters supported here

        Raises:
            HTTPNoContent: on success response

        Examples:
            Example of command by using curl::

                $ curl -v -XPOST 'http://example.com/api/v1/packages'
                > POST /api/v1/packages HTTP/1.1
                > Host: example.com
                > User-Agent: curl/7.86.0
                > Accept: */*
                >
                < HTTP/1.1 204 No Content
                < Date: Wed, 23 Nov 2022 19:38:06 GMT
                < Server: Python/3.10 aiohttp/3.8.3
                <
        """
        self.service.load()

        raise HTTPNoContent()
