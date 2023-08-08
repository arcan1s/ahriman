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
from ahriman.web.views.service.add import AddView
from ahriman.web.views.service.pgp import PGPView
from ahriman.web.views.service.process import ProcessView
from ahriman.web.views.service.rebuild import RebuildView
from ahriman.web.views.service.remove import RemoveView
from ahriman.web.views.service.request import RequestView
from ahriman.web.views.service.search import SearchView
from ahriman.web.views.service.update import UpdateView
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

    Args:
        application(Application): web application instance
        static_path(Path): path to static files directory
    """
    application.router.add_view("/", IndexView)
    application.router.add_view("/index.html", IndexView)

    application.router.add_view("/api-docs", DocsView)
    application.router.add_view("/api-docs/swagger.json", SwaggerView)

    application.router.add_static("/static", static_path, follow_symlinks=True)

    application.router.add_view("/api/v1/service/add", AddView)
    application.router.add_view("/api/v1/service/pgp", PGPView)
    application.router.add_view("/api/v1/service/rebuild", RebuildView)
    application.router.add_view("/api/v1/service/process/{process_id}", ProcessView)
    application.router.add_view("/api/v1/service/remove", RemoveView)
    application.router.add_view("/api/v1/service/request", RequestView)
    application.router.add_view("/api/v1/service/search", SearchView)
    application.router.add_view("/api/v1/service/update", UpdateView)

    application.router.add_view("/api/v1/packages", PackagesView)
    application.router.add_view("/api/v1/packages/{package}", PackageView)
    application.router.add_view("/api/v1/packages/{package}/logs", LogsView)

    application.router.add_view("/api/v1/status", StatusView)

    application.router.add_view("/api/v1/login", LoginView)
    application.router.add_view("/api/v1/logout", LogoutView)
