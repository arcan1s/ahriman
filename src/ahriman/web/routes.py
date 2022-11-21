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
from aiohttp.web import Application
from pathlib import Path

from ahriman.web.views.index import IndexView
from ahriman.web.views.service.add import AddView
from ahriman.web.views.service.remove import RemoveView
from ahriman.web.views.service.request import RequestView
from ahriman.web.views.service.search import SearchView
from ahriman.web.views.status.logs import LogsView
from ahriman.web.views.status.package import PackageView
from ahriman.web.views.status.packages import PackagesView
from ahriman.web.views.status.status import StatusView
from ahriman.web.views.user.login import LoginView
from ahriman.web.views.user.logout import LogoutView


__all__ = ["setup_routes"]


def setup_routes(application: Application, static_path: Path) -> None:
    """
    setup all defined routes

    Available routes are:

        * ``GET /`` get build status page
        * ``GET /index.html`` same as above

        * ``POST /api/v1/service/add`` add new packages to repository

        * ``POST /api/v1/service/remove`` remove existing package from repository

        * ``POST /api/v1/service/request`` request to add new packages to repository

        * ``GET /api/v1/service/search`` search for substring in AUR

        * ``POST /api/v1/service/update`` update packages in repository, actually it is just alias for add

        * ``GET /api/v1/packages`` get all known packages
        * ``POST /api/v1/packages`` force update every package from repository

        * ``DELETE /api/v1/package/:base`` delete package base from status page
        * ``GET /api/v1/package/:base`` get package base status
        * ``POST /api/v1/package/:base`` update package base status

        * ``DELETE /api/v1/packages/{package}/logs`` delete package related logs
        * ``GET /api/v1/packages/{package}/logs`` create log record for the package
        * ``POST /api/v1/packages/{package}/logs`` get last package logs

        * ``GET /api/v1/status`` get service status itself
        * ``POST /api/v1/status`` update service status itself

        * ``GET /api/v1/login`` OAuth2 handler for login
        * ``POST /api/v1/login`` login to service
        * ``POST /api/v1/logout`` logout from service

    Args:
        application(Application): web application instance
        static_path(Path): path to static files directory
    """
    application.router.add_get("/", IndexView, allow_head=True)
    application.router.add_get("/index.html", IndexView, allow_head=True)

    application.router.add_static("/static", static_path, follow_symlinks=True)

    application.router.add_post("/api/v1/service/add", AddView)

    application.router.add_post("/api/v1/service/remove", RemoveView)

    application.router.add_post("/api/v1/service/request", RequestView)

    application.router.add_get("/api/v1/service/search", SearchView, allow_head=False)

    application.router.add_post("/api/v1/service/update", AddView)

    application.router.add_get("/api/v1/packages", PackagesView, allow_head=True)
    application.router.add_post("/api/v1/packages", PackagesView)

    application.router.add_delete("/api/v1/packages/{package}", PackageView)
    application.router.add_get("/api/v1/packages/{package}", PackageView, allow_head=True)
    application.router.add_post("/api/v1/packages/{package}", PackageView)

    application.router.add_delete("/api/v1/packages/{package}/logs", LogsView)
    application.router.add_get("/api/v1/packages/{package}/logs", LogsView, allow_head=True)
    application.router.add_post("/api/v1/packages/{package}/logs", LogsView)

    application.router.add_get("/api/v1/status", StatusView, allow_head=True)
    application.router.add_post("/api/v1/status", StatusView)

    application.router.add_get("/api/v1/login", LoginView)
    application.router.add_post("/api/v1/login", LoginView)
    application.router.add_post("/api/v1/logout", LogoutView)
