#
# Copyright (c) 2021-2024 ahriman team.
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
from aiohttp.web import Application, View

import ahriman.web.views

from ahriman.core.configuration import Configuration
from ahriman.core.module_loader import implementations
from ahriman.web.views.base import BaseView


__all__ = ["setup_routes"]


def _dynamic_routes(configuration: Configuration) -> dict[str, type[View]]:
    """
    extract dynamic routes based on views

    Args:
        configuration(Configuration): configuration instance

    Returns:
        dict[str, type[View]]: map of the route to its view
    """
    routes: dict[str, type[View]] = {}
    for view in implementations(ahriman.web.views, BaseView):
        view_routes = view.routes(configuration)
        routes.update([(route, view) for route in view_routes])

    return routes


def setup_routes(application: Application, configuration: Configuration) -> None:
    """
    setup all defined routes

    Args:
        application(Application): web application instance
        configuration(Configuration): configuration instance
    """
    application.router.add_static("/static", configuration.getpath("web", "static_path"), follow_symlinks=True)

    for route, view in _dynamic_routes(configuration).items():
        application.router.add_view(route, view)
