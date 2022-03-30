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
from aiohttp.web import Response, json_response

from ahriman import version
from ahriman.models.counters import Counters
from ahriman.models.internal_status import InternalStatus
from ahriman.models.user_access import UserAccess
from ahriman.web.views.base import BaseView


class StatusView(BaseView):
    """
    web service status web view
    :cvar GET_PERMISSION: get permissions of self
    :cvar HEAD_PERMISSION: head permissions of self
    """

    GET_PERMISSION = HEAD_PERMISSION = UserAccess.Read

    async def get(self) -> Response:
        """
        get current service status
        :return: 200 with service status object
        """
        counters = Counters.from_packages(self.service.packages)
        status = InternalStatus(
            architecture=self.service.architecture,
            packages=counters,
            repository=self.service.repository.name,
            version=version.__version__)

        return json_response(status.view())
