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
import aiohttp_jinja2

from typing import Any, Dict

from ahriman import version
from ahriman.core.auth.helpers import authorized_userid
from ahriman.core.util import pretty_datetime
from ahriman.models.user_access import UserAccess
from ahriman.web.views.base import BaseView


class IndexView(BaseView):
    """
    root view

    It uses jinja2 templates for report generation, the following variables are allowed:

        * architecture - repository architecture, string, required
        * auth - authorization descriptor, required
            * authenticated - alias to check if user can see the page, boolean, required
            * control - HTML to insert for login control, HTML string, required
            * enabled - whether authorization is enabled by configuration or not, boolean, required
            * username - authenticated username if any, string, null means not authenticated
        * index_url - url to the repository index, string, optional
        * packages - sorted list of packages properties, required
            * base, string
            * depends, sorted list of strings
            * groups, sorted list of strings
            * licenses, sorted list of strings
            * packages, sorted list of strings
            * status, string based on enum value
            * status_color, string based on enum value
            * timestamp, pretty printed datetime, string
            * version, string
            * web_url, string
        * repository - repository name, string, required
        * service - service status properties, required
            * status, string based on enum value
            * status_color, string based on enum value
            * timestamp, pretty printed datetime, string
        * version - ahriman version, string, required

    Attributes:
        GET_PERMISSION(UserAccess): (class attribute) get permissions of self
        HEAD_PERMISSION(UserAccess): (class attribute) head permissions of self
    """

    GET_PERMISSION = HEAD_PERMISSION = UserAccess.Safe

    @aiohttp_jinja2.template("build-status.jinja2")
    async def get(self) -> Dict[str, Any]:
        """
        process get request. No parameters supported here

        Returns:
            Dict[str, Any]: parameters for jinja template
        """
        # some magic to make it jinja-friendly
        packages = [
            {
                "base": package.base,
                "depends": package.depends,
                "groups": package.groups,
                "licenses": package.licenses,
                "packages": list(sorted(package.packages)),
                "status": status.status.value,
                "status_color": status.status.bootstrap_color(),
                "timestamp": pretty_datetime(status.timestamp),
                "version": package.version,
                "web_url": package.web_url,
            } for package, status in sorted(self.service.packages, key=lambda item: item[0].base)
        ]
        service = {
            "status": self.service.status.status.value,
            "status_color": self.service.status.status.badges_color(),
            "timestamp": pretty_datetime(self.service.status.timestamp),
        }

        # auth block
        auth_username = await authorized_userid(self.request)
        authenticated = not self.validator.enabled or self.validator.safe_build_status or auth_username is not None
        auth = {
            "authenticated": authenticated,
            "control": self.validator.auth_control,
            "enabled": self.validator.enabled,
            "username": auth_username,
        }

        return {
            "architecture": self.service.architecture,
            "auth": auth,
            "index_url": self.configuration.get("web", "index_url", fallback=None),
            "packages": packages,
            "repository": self.service.repository.name,
            "service": service,
            "version": version.__version__,
        }
