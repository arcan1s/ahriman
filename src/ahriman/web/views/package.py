#
# Copyright (c) 2021 Evgenii Alekseev.
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
from aiohttp.web import HTTPOk, Response

from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.package import Package
from ahriman.web.views.base import BaseView


class PackageView(BaseView):

    async def delete(self) -> Response:
        base = self.request.match_info['package']
        self.service.remove(base)

        return HTTPOk()

    async def post(self) -> Response:
        base = self.request.match_info['package']
        data = await self.request.json()

        package = Package(**data['package']) if 'package' in data else None
        status = BuildStatusEnum(data['status'])
        self.service.update(base, status, package)

        return HTTPOk()
