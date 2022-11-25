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
from aiohttp.web import HTTPBadRequest, HTTPNoContent, HTTPNotFound, Response, json_response

from ahriman.models.user_access import UserAccess
from ahriman.web.views.base import BaseView


class PGPView(BaseView):
    """
    pgp key management web view

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
        HEAD_PERMISSION(UserAccess): (class attribute) head permissions of self
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    POST_PERMISSION = UserAccess.Full
    GET_PERMISSION = HEAD_PERMISSION = UserAccess.Reporter

    async def get(self) -> Response:
        """
        retrieve key from the key server. It supports two query parameters: ``key`` - pgp key fingerprint and
        ``server`` which points to valid PGP key server

        Returns:
            Response: 200 with key body on success

        Raises:
            HTTPBadRequest: if bad data is supplied
            HTTPNotFound: if key wasn't found or service was unable to fetch it

        Examples:
            Example of command by using curl::

                $ curl -v -H 'Accept: application/json' 'http://example.com/api/v1/service/pgp?key=0xE989490C&server=keyserver.ubuntu.com'
                > GET /api/v1/service/pgp?key=0xE989490C&server=keyserver.ubuntu.com HTTP/1.1
                > Host: example.com
                > User-Agent: curl/7.86.0
                > Accept: application/json
                >
                < HTTP/1.1 200 OK
                < Content-Type: application/json; charset=utf-8
                < Content-Length: 3275
                < Date: Fri, 25 Nov 2022 22:54:02 GMT
                < Server: Python/3.10 aiohttp/3.8.3
                <
                {"key": "key"}
                        """
        try:
            key = self.get_non_empty(self.request.query.getone, "key")
            server = self.get_non_empty(self.request.query.getone, "server")
        except Exception as e:
            raise HTTPBadRequest(reason=str(e))

        try:
            key = self.service.repository.sign.key_download(server, key)
        except Exception:
            raise HTTPNotFound()

        return json_response({"key": key})

    async def post(self) -> None:
        """
        store key to the local service environment

        JSON body must be supplied, the following model is used::

            {
                "key": "0x8BE91E5A773FB48AC05CC1EDBED105AED6246B39",  # key fingerprint to import
                "server": "keyserver.ubuntu.com"                      # optional pgp server address
            }

        Raises:
            HTTPBadRequest: if bad data is supplied
            HTTPNoContent: in case of success response

        Examples:
            Example of command by using curl::

                $ curl -v -H 'Content-Type: application/json' 'http://example.com/api/v1/service/pgp' -d '{"key": "0xE989490C"}'
                > POST /api/v1/service/pgp HTTP/1.1
                > Host: example.com
                > User-Agent: curl/7.86.0
                > Accept: */*
                > Content-Type: application/json
                > Content-Length: 21
                >
                < HTTP/1.1 204 No Content
                < Date: Fri, 25 Nov 2022 22:55:56 GMT
                < Server: Python/3.10 aiohttp/3.8.3
                <
        """
        data = await self.extract_data()

        try:
            key = self.get_non_empty(data.get, "key")
        except Exception as e:
            raise HTTPBadRequest(reason=str(e))

        self.spawner.key_import(key, data.get("server"))

        raise HTTPNoContent()
