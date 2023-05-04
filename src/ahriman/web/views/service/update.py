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

from aiohttp.web import HTTPNoContent

from ahriman.models.user_access import UserAccess
from ahriman.web.schemas.auth_schema import AuthSchema
from ahriman.web.schemas.error_schema import ErrorSchema
from ahriman.web.views.base import BaseView


class UpdateView(BaseView):
    """
    update repository web view

    Attributes:
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    POST_PERMISSION = UserAccess.Full

    @aiohttp_apispec.docs(
        tags=["Actions"],
        summary="Update packages",
        description="Run repository update process",
        responses={
            204: {"description": "Success response"},
            401: {"description": "Authorization required", "schema": ErrorSchema},
            403: {"description": "Access is forbidden", "schema": ErrorSchema},
            500: {"description": "Internal server error", "schema": ErrorSchema},
        },
        security=[{"token": [POST_PERMISSION]}],
    )
    @aiohttp_apispec.cookies_schema(AuthSchema)
    async def post(self) -> None:
        """
        run repository update. No parameters supported here

        Raises:
            HTTPNoContent: in case of success response
        """
        self.spawner.packages_update()

        raise HTTPNoContent()
