#
# Copyright (c) 2021-2025 ahriman team.
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
from typing import ClassVar

from ahriman.models.user_access import UserAccess
from ahriman.web.apispec.decorators import apidocs
from ahriman.web.schemas import PGPKeyIdSchema, PGPKeySchema, ProcessIdSchema
from ahriman.web.views.base import BaseView


class PGPView(BaseView):
    """
    pgp key management web view

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    GET_PERMISSION: ClassVar[UserAccess] = UserAccess.Reporter
    POST_PERMISSION: ClassVar[UserAccess] = UserAccess.Full
    ROUTES = ["/api/v1/service/pgp"]

    @apidocs(
        tags=["Actions"],
        summary="Search for PGP key",
        description="Search for PGP key and retrieve its body",
        permission=GET_PERMISSION,
        error_400_enabled=True,
        error_404_description="PGP key is unknown",
        schema=PGPKeySchema,
        query_schema=PGPKeyIdSchema,
    )
    async def get(self) -> Response:
        """
        retrieve key from the key server

        Returns:
            Response: 200 with key body on success

        Raises:
            HTTPBadRequest: if bad data is supplied
            HTTPNotFound: if key wasn't found or service was unable to fetch it
        """
        try:
            key = self.get_non_empty(self.request.query.get, "key")
            server = self.get_non_empty(self.request.query.get, "server")
        except Exception as ex:
            raise HTTPBadRequest(reason=str(ex))

        try:
            key = self.sign.key_download(server, key)
        except Exception:
            raise HTTPNotFound(reason=f"Key {key} is unknown")

        return json_response({"key": key})

    @apidocs(
        tags=["Actions"],
        summary="Fetch PGP key",
        description="Fetch PGP key from the key server",
        permission=POST_PERMISSION,
        error_400_enabled=True,
        schema=ProcessIdSchema,
        body_schema=PGPKeyIdSchema,
    )
    async def post(self) -> Response:
        """
        store key to the local service environment

        Returns:
            Response: 200 with spawned process id

        Raises:
            HTTPBadRequest: if bad data is supplied
        """
        try:
            data = await self.request.json()
            key = self.get_non_empty(data.get, "key")
        except Exception as ex:
            raise HTTPBadRequest(reason=str(ex))

        process_id = self.spawner.key_import(key, data.get("server"))

        return json_response({"process_id": process_id})
