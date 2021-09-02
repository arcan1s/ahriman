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
from aiohttp.web import Application

from ahriman.web.views.ahriman import AhrimanView
from ahriman.web.views.index import IndexView
from ahriman.web.views.login import LoginView
from ahriman.web.views.logout import LogoutView
from ahriman.web.views.package import PackageView
from ahriman.web.views.packages import PackagesView
from ahriman.web.views.status import StatusView


def setup_routes(application: Application) -> None:
    """
    setup all defined routes

    Available routes are:

        GET /                           get build status page
        GET /index.html                 same as above

        POST /login                     login to service
        POST /logout                    logout from service

        GET /api/v1/ahriman             get current service status
        POST /api/v1/ahriman            update service status

        GET /api/v1/packages            get all known packages
        POST /api/v1/packages           force update every package from repository

        DELETE /api/v1/package/:base    delete package base from status page
        GET /api/v1/package/:base       get package base status
        POST /api/v1/package/:base      update package base status

        GET /api/v1/status              get web service status itself

    :param application: web application instance
    """
    application.router.add_get("/", IndexView)
    application.router.add_get("/index.html", IndexView)

    application.router.add_post("/login", LoginView)
    application.router.add_post("/logout", LogoutView)

    application.router.add_get("/api/v1/ahriman", AhrimanView)
    application.router.add_post("/api/v1/ahriman", AhrimanView)

    application.router.add_get("/api/v1/packages", PackagesView)
    application.router.add_post("/api/v1/packages", PackagesView)

    application.router.add_delete("/api/v1/packages/{package}", PackageView)
    application.router.add_get("/api/v1/packages/{package}", PackageView)
    application.router.add_post("/api/v1/packages/{package}", PackageView)

    application.router.add_get("/api/v1/status", StatusView)
