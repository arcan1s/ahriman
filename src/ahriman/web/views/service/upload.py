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
import shutil
import tempfile

from aiohttp import BodyPartReader
from aiohttp.web import HTTPBadRequest, HTTPCreated, HTTPNotFound
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
            404: {"description": "Not found", "schema": ErrorSchema},
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
        if not self.configuration.getboolean("web", "enable_archive_upload", fallback=False):
            raise HTTPNotFound()

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

        max_body_size = self.configuration.getint("web", "max_body_size", fallback=None)
        current_size = 0

        # in order to handle errors automatically we create temporary file for long operation (transfer) and then copy
        # it to valid location
        with tempfile.NamedTemporaryFile() as cache:
            while True:
                chunk = await part.read_chunk()
                if not chunk:
                    break

                current_size += len(chunk)
                if max_body_size is not None and current_size > max_body_size:
                    raise HTTPBadRequest(reason="Body part is too large")

                cache.write(chunk)

            # and now copy temporary file to correct location
            cache.seek(0)  # reset file position
            output = self.configuration.repository_paths.packages / archive_name
            with output.open("wb") as archive:
                shutil.copyfileobj(cache, archive)

        raise HTTPCreated()
