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
from aiohttp.web import Response, json_response
from collections.abc import Callable

from ahriman.core.util import partition
from ahriman.models.user_access import UserAccess
from ahriman.web.views.base import BaseView


class SwaggerView(BaseView):
    """
    api docs specification view

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
    """

    GET_PERMISSION = UserAccess.Unauthorized
    ROUTES = ["/api-docs/swagger.json"]

    async def get(self) -> Response:
        """
        get api specification

        Returns:
            Response: 200 with json api specification
        """
        spec = self.request.app["swagger_dict"]
        is_body_parameter: Callable[[dict[str, str]], bool] = lambda p: p["in"] == "body" or p["in"] == "formData"

        # special workaround because it writes request body to parameters section
        paths = spec["paths"]
        for methods in paths.values():
            for method in methods.values():
                if "parameters" not in method:
                    continue

                body, other = partition(method["parameters"], is_body_parameter)
                if not body:
                    continue  # there were no ``body`` parameters found

                schema = next(iter(body))
                content_type = "multipart/form-data" if schema["in"] == "formData" else "application/json"

                # there should be only one body parameters
                method["requestBody"] = {
                    "content": {
                        content_type: {
                            "schema": schema["schema"]
                        }
                    }
                }
                method["parameters"] = other

        # inject security schema
        spec["components"]["securitySchemes"] = {
            key: value
            for schema in spec["security"]
            for key, value in schema.items()
        }

        return json_response(spec)
