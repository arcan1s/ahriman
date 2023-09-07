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
from aiohttp.web import Application
from pathlib import Path

from ahriman.web.views.api.docs import DocsView
from ahriman.web.views.api.swagger import SwaggerView
from ahriman.web.views.index import IndexView
from ahriman.web.views import v1, v2


__all__ = ["setup_routes"]


def setup_routes(application: Application, static_path: Path) -> None:
    """
    setup all defined routes

    Args:
        application(Application): web application instance
        static_path(Path): path to static files directory
    """
    application.router.add_view("/", IndexView)
    application.router.add_view("/index.html", IndexView)

    application.router.add_view("/api-docs", DocsView)
    application.router.add_view("/api-docs/swagger.json", SwaggerView)

    application.router.add_static("/static", static_path, follow_symlinks=True)

    application.router.add_view("/api/v1/service/add", v1.AddView)
    application.router.add_view("/api/v1/service/pgp", v1.PGPView)
    application.router.add_view("/api/v1/service/rebuild", v1.RebuildView)
    application.router.add_view("/api/v1/service/process/{process_id}", v1.ProcessView)
    application.router.add_view("/api/v1/service/remove", v1.RemoveView)
    application.router.add_view("/api/v1/service/request", v1.RequestView)
    application.router.add_view("/api/v1/service/search", v1.SearchView)
    application.router.add_view("/api/v1/service/update", v1.UpdateView)
    application.router.add_view("/api/v1/service/upload", v1.UploadView)

    application.router.add_view("/api/v1/packages", v1.PackagesView)
    application.router.add_view("/api/v1/packages/{package}", v1.PackageView)
    application.router.add_view("/api/v1/packages/{package}/logs", v1.LogsView)
    application.router.add_view("/api/v2/packages/{package}/logs", v2.LogsView)

    application.router.add_view("/api/v1/status", v1.StatusView)

    application.router.add_view("/api/v1/login", v1.LoginView)
    application.router.add_view("/api/v1/logout", v1.LogoutView)
