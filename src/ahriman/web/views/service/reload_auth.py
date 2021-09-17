#
# Copyright (c) 2021 ahriman team.
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
from aiohttp.web import Response
from aiohttp.web_exceptions import HTTPNoContent

from ahriman.core.auth.auth import Auth
from ahriman.web.views.base import BaseView


class ReloadAuthView(BaseView):
    """
    reload authentication module web view
    """

    async def post(self) -> Response:
        """
        reload authentication module. No parameters supported here
        :return: 204 on success
        """
        self.configuration.reload()

        try:
            import aiohttp_security  # type: ignore
            self.request.app[aiohttp_security.api.AUTZ_KEY].validator =\
                self.request.app["validator"] =\
                Auth.load(self.configuration)
        except (ImportError, KeyError):
            self.request.app.logger.warning("could not update authentication module validator", exc_info=True)
            raise

        return HTTPNoContent()
