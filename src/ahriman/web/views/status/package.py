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
from aiohttp.web import HTTPBadRequest, HTTPNoContent, HTTPNotFound, Response, json_response

from ahriman.core.exceptions import UnknownPackageError
from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.package import Package
from ahriman.models.user_access import UserAccess
from ahriman.web.views.base import BaseView


class PackageView(BaseView):
    """
    package base specific web view

    Attributes:
        DELETE_PERMISSION(UserAccess): (class attribute) delete permissions of self
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
        HEAD_PERMISSION(UserAccess): (class attribute) head permissions of self
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    DELETE_PERMISSION = POST_PERMISSION = UserAccess.Full
    GET_PERMISSION = HEAD_PERMISSION = UserAccess.Read

    async def delete(self) -> None:
        """
        delete package base from status page

        Raises:
            HTTPNoContent: on success response

        Examples:
            Example of command by using curl::

                $ curl -v -XDELETE 'http://example.com/api/v1/packages/ahriman'
                > DELETE /api/v1/packages/ahriman HTTP/1.1
                > Host: example.com
                > User-Agent: curl/7.86.0
                > Accept: */*
                >
                < HTTP/1.1 204 No Content
                < Date: Wed, 23 Nov 2022 19:43:40 GMT
                < Server: Python/3.10 aiohttp/3.8.3
                <
        """
        package_base = self.request.match_info["package"]
        self.service.remove(package_base)

        raise HTTPNoContent()

    async def get(self) -> Response:
        """
        get current package base status

        Returns:
            Response: 200 with package description on success

        Raises:
            HTTPNotFound: if no package was found

        Examples:
            Example of command by using curl::

                $ curl -v -H 'Accept: application/json' 'http://example.com/api/v1/packages/ahriman'
                > GET /api/v1/packages/ahriman HTTP/1.1
                > Host: example.com
                > User-Agent: curl/7.86.0
                > Accept: application/json
                >
                < HTTP/1.1 200 OK
                < Content-Type: application/json; charset=utf-8
                < Content-Length: 743
                < Date: Wed, 23 Nov 2022 19:41:01 GMT
                < Server: Python/3.10 aiohttp/3.8.3
                <
                [{"package": {"base": "ahriman", "version": "2.3.0-1", "remote": {"git_url": "https://aur.archlinux.org/ahriman.git", "web_url": "https://aur.archlinux.org/packages/ahriman", "path": ".", "branch": "master", "source": "aur"}, "packages": {"ahriman": {"architecture": "any", "archive_size": 247573, "build_date": 1669231069, "depends": ["devtools", "git", "pyalpm", "python-inflection", "python-passlib", "python-requests", "python-setuptools", "python-srcinfo"], "description": "ArcH linux ReposItory MANager", "filename": "ahriman-2.3.0-1-any.pkg.tar.zst", "groups": [], "installed_size": 1676153, "licenses": ["GPL3"], "provides": [], "url": "https://github.com/arcan1s/ahriman"}}}, "status": {"status": "success", "timestamp": 1669231136}}]
        """
        package_base = self.request.match_info["package"]

        try:
            package, status = self.service.get(package_base)
        except UnknownPackageError:
            raise HTTPNotFound()

        response = [
            {
                "package": package.view(),
                "status": status.view()
            }
        ]
        return json_response(response)

    async def post(self) -> None:
        """
        update package build status

        JSON body must be supplied, the following model is used::

            {
                "status": "unknown",   # package build status string, must be valid ``BuildStatusEnum``
                "package": {}          # package body (use ``dataclasses.asdict`` to generate one), optional.
                                       # Must be supplied in case if package base is unknown
            }

        Raises:
            HTTPBadRequest: if bad data is supplied
            HTTPNoContent: in case of success response

        Examples:
            Example of command by using curl::

                $ curl -v -H 'Content-Type: application/json' 'http://example.com/api/v1/packages/ahriman' -d '{"status": "success"}'
                > POST /api/v1/packages/ahriman HTTP/1.1
                > Host: example.com
                > User-Agent: curl/7.86.0
                > Accept: */*
                > Content-Type: application/json
                > Content-Length: 21
                >
                < HTTP/1.1 204 No Content
                < Date: Wed, 23 Nov 2022 19:42:49 GMT
                < Server: Python/3.10 aiohttp/3.8.3
                <
        """
        package_base = self.request.match_info["package"]
        data = await self.extract_data()

        try:
            package = Package.from_json(data["package"]) if "package" in data else None
            status = BuildStatusEnum(data["status"])
        except Exception as e:
            raise HTTPBadRequest(reason=str(e))

        try:
            self.service.update(package_base, status, package)
        except UnknownPackageError:
            raise HTTPBadRequest(reason=f"Package {package_base} is unknown, but no package body set")

        raise HTTPNoContent()
