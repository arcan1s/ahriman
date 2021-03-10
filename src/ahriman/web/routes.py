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
from aiohttp.web import Application

from ahriman.web.views.index import IndexView
from ahriman.web.views.package import PackageView
from ahriman.web.views.packages import PackagesView


def setup_routes(app: Application) -> None:
    app.router.add_get('/', IndexView)
    app.router.add_get('/index.html', IndexView)

    app.router.add_post('/api/v1/packages', PackagesView)

    app.router.add_delete('/api/v1/packages/{package}', PackageView)
    app.router.add_post('/api/v1/packages/{package}', PackageView)