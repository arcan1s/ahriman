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
from aiohttp.web import HTTPNoContent, Response, json_response
from typing import ClassVar

from ahriman.core.formatters import ConfigurationPrinter
from ahriman.models.user_access import UserAccess
from ahriman.web.apispec.decorators import apidocs
from ahriman.web.schemas import ConfigurationSchema
from ahriman.web.views.base import BaseView


class ConfigView(BaseView):
    """
    configuration control view

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
        POST_PERMISSION(UserAccess): (class attribute) post permissions of self
    """

    GET_PERMISSION = POST_PERMISSION = UserAccess.Full  # type: ClassVar[UserAccess]
    ROUTES = ["/api/v1/service/config"]

    @apidocs(
        tags=["Actions"],
        summary="Get configuration",
        description="Get current web service configuration as nested dictionary",
        permission=GET_PERMISSION,
        schema=ConfigurationSchema(many=True),
    )
    async def get(self) -> Response:
        """
        get current web service configuration

        Returns:
            Response: current web service configuration as nested dictionary
        """
        dump = self.configuration.dump()

        response = [
            {
                "section": section,
                "key": key,
                "value": value,
            } for section, values in dump.items()
            for key, value in values.items()
            if key not in ConfigurationPrinter.HIDE_KEYS
        ]
        return json_response(response)

    @apidocs(
        tags=["Actions"],
        summary="Reload configuration",
        description="Reload configuration from current files",
        permission=POST_PERMISSION,
    )
    async def post(self) -> None:
        """
        reload web service configuration

        Raises:
            HTTPNoContent: on success response
        """
        self.configuration.reload()

        raise HTTPNoContent
