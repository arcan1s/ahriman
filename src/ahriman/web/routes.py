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


def setup_routes(application: Application) -> None:
    '''
    setup all defined routes

    Available routes are:

        GET /                           get build status page
        GET /index.html                 same as above

        POST /api/v1/packages           force update every package from repository

        POST /api/v1/package/:base      update package base status
        DELETE /api/v1/package/:base    delete package base from status page

    :param application: web application instance
    '''
    application.router.add_get('/', IndexView)
    application.router.add_get('/index.html', IndexView)

    application.router.add_post('/api/v1/packages', PackagesView)

    application.router.add_delete('/api/v1/packages/{package}', PackageView)
    application.router.add_post('/api/v1/packages/{package}', PackageView)
