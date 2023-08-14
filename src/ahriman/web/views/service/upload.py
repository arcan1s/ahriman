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
import aiohttp_apispec  # type: ignore[import]

from aiohttp import BodyPartReader
from aiohttp.web import HTTPBadRequest, HTTPCreated
from pathlib import Path

from ahriman.models.user_access import UserAccess
from ahriman.web.schemas import AuthSchema, ErrorSchema, FileSchema
from ahriman.web.views.base import BaseView


class UploadView(BaseView):
    """
    upload file to repository

    Attributes:
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    POST_PERMISSION = UserAccess.Full

    @aiohttp_apispec.docs(
        tags=["Actions"],
        summary="Upload package",
        description="Upload package to local filesystem",
        responses={
            201: {"description": "Success response"},
            400: {"description": "Bad data is supplied", "schema": ErrorSchema},
            401: {"description": "Authorization required", "schema": ErrorSchema},
            403: {"description": "Access is forbidden", "schema": ErrorSchema},
            500: {"description": "Internal server error", "schema": ErrorSchema},
        },
        security=[{"token": [POST_PERMISSION]}],
    )
    @aiohttp_apispec.cookies_schema(AuthSchema)
    @aiohttp_apispec.form_schema(FileSchema)
    async def post(self) -> None:
        """
        upload file from another instance to the server

        Raises:
            HTTPBadRequest: if bad data is supplied
            HTTPCreated: on success response
        """
        try:
            reader = await self.request.multipart()
        except Exception as e:
            raise HTTPBadRequest(reason=str(e))

        part = await reader.next()
        if not isinstance(part, BodyPartReader):
            raise HTTPBadRequest(reason="Invalid multipart message received")

        if part.name != "archive":
            raise HTTPBadRequest(reason="Multipart field isn't archive")

        archive_name = part.filename
        if archive_name is None:
            raise HTTPBadRequest(reason="Filename must be set")  # pragma: no cover
        # some magic inside. We would like to make sure that passed filename is filename
        # without slashes, dots, etc
        if Path(archive_name).resolve().name != archive_name:
            raise HTTPBadRequest(reason="Filename must be valid archive name")

        output = self.configuration.repository_paths.packages / archive_name
        with output.open("wb") as archive:
            while True:
                chunk = await part.read_chunk()
                if not chunk:
                    break
                archive.write(chunk)

        raise HTTPCreated()
