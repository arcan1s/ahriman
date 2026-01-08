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
from aiohttp.web import HTTPBadRequest, HTTPNoContent
from typing import ClassVar

from ahriman.models.user_access import UserAccess
from ahriman.web.apispec.decorators import apidocs
from ahriman.web.schemas import LogsRotateSchema
from ahriman.web.views.base import BaseView


class LogsView(BaseView):
    """
    logs management web view

    Attributes:
        DELETE_PERMISSION(UserAccess): (class attribute) delete permissions of self
    """

    DELETE_PERMISSION: ClassVar[UserAccess] = UserAccess.Full
    ROUTES = ["/api/v1/service/logs"]

    @apidocs(
        tags=["Actions"],
        summary="Rotate logs",
        description="Remove older logs from system",
        permission=DELETE_PERMISSION,
        error_400_enabled=True,
        error_404_description="Repository is unknown",
        query_schema=LogsRotateSchema,
    )
    async def delete(self) -> None:
        """
        rotate logs from system

        Raises:
            HTTPBadRequest: if bad data is supplied
            HTTPNoContent: on success response
        """
        try:
            keep_last_records = int(self.request.query.get("keep_last_records", 0))
        except Exception as ex:
            raise HTTPBadRequest(reason=str(ex))

        self.service().logs_rotate(keep_last_records)

        raise HTTPNoContent
