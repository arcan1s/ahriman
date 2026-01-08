#
# Copyright (c) 2021-2026 ahriman team.
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
import shutil

from aiohttp import BodyPartReader
from aiohttp.web import HTTPBadRequest, HTTPCreated
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import ClassVar

from ahriman.core.configuration import Configuration
from ahriman.models.repository_paths import RepositoryPaths
from ahriman.models.user_access import UserAccess
from ahriman.web.apispec.decorators import apidocs
from ahriman.web.schemas import FileSchema, RepositoryIdSchema
from ahriman.web.views.base import BaseView


class UploadView(BaseView):
    """
    upload file to repository

    Attributes:
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    POST_PERMISSION: ClassVar[UserAccess] = UserAccess.Full
    ROUTES = ["/api/v1/service/upload"]

    @classmethod
    def routes(cls, configuration: Configuration) -> list[str]:
        """
        extract routes list for the view

        Args:
            configuration(Configuration): configuration instance

        Returns:
            list[str]: list of routes defined for the view. By default, it tries to read :attr:`ROUTES` option if set
            and returns empty list otherwise
        """
        if not configuration.getboolean("web", "enable_archive_upload", fallback=False):
            return []
        return cls.ROUTES

    @staticmethod
    async def save_file(part: BodyPartReader, target: Path, *, max_body_size: int | None = None) -> tuple[str, Path]:
        """
        save file to local cache

        Args:
            part(BodyPartReader): multipart part to be saved
            target(Path): path to directory to which file should be saved
            max_body_size(int | None, optional): max body size in bytes (Default value = None)

        Returns:
            tuple[str, Path]: map of received filename to its local path

        Raises:
            HTTPBadRequest: if bad data is supplied
        """
        archive_name = part.filename
        if archive_name is None:
            raise HTTPBadRequest(reason="Filename must be set")
        # some magic inside. We would like to make sure that passed filename is filename
        # without slashes, dots, etc
        if Path(archive_name).resolve().name != archive_name:
            raise HTTPBadRequest(reason="Filename must be valid archive name")

        current_size = 0

        # in order to handle errors automatically we create temporary file for long operation (transfer)
        # and then copy it to valid location
        with NamedTemporaryFile() as cache:
            while True:
                chunk = await part.read_chunk()
                if not chunk:
                    break

                current_size += len(chunk)
                if max_body_size is not None and current_size > max_body_size:
                    raise HTTPBadRequest(reason="Body part is too large")

                cache.write(chunk)

            cache.seek(0)  # reset file position

            # and now copy temporary file to target location as hidden file
            # we put it as hidden in order to make sure that it will not be handled during some random process
            temporary_output = target / f".{archive_name}"
            with temporary_output.open("wb") as archive:
                shutil.copyfileobj(cache, archive)

            return archive_name, temporary_output

    @apidocs(
        tags=["Actions"],
        summary="Upload package",
        description="Upload package to local filesystem",
        permission=POST_PERMISSION,
        response_code=HTTPCreated,
        error_400_enabled=True,
        error_404_description="Repository is unknown",
        query_schema=RepositoryIdSchema,
        body_schema=FileSchema,
        body_location="form",
    )
    async def post(self) -> None:
        """
        upload file from another instance to the server

        Raises:
            HTTPBadRequest: if bad data is supplied
            HTTPCreated: on success response
            HTTPNotFound: method is disabled by configuration
        """
        try:
            reader = await self.request.multipart()
        except Exception as ex:
            raise HTTPBadRequest(reason=str(ex))

        max_body_size = self.configuration.getint("web", "max_body_size", fallback=None)

        paths_root = self.configuration.repository_paths.root
        repository_id = self.repository_id()
        target = RepositoryPaths(paths_root, repository_id).packages

        files = []
        while (part := await reader.next()) is not None:
            if not isinstance(part, BodyPartReader):
                raise HTTPBadRequest(reason="Invalid multipart message received")

            if part.name not in ("package", "signature"):
                raise HTTPBadRequest(reason="Multipart field isn't package or signature")

            files.append(await self.save_file(part, target, max_body_size=max_body_size))

        # and now we can rename files, which is relatively fast operation
        # it is probably good way to call lock here, however
        for filename, current_location in files:
            target_location = current_location.parent / filename
            current_location.rename(target_location)

        raise HTTPCreated
