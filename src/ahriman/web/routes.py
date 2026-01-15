#
# Copyright (c) 2021-2025 ahriman team.
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
import re

from aiohttp.web import Application, View
from collections.abc import Iterator

import ahriman.web.views

from ahriman.core.configuration import Configuration
from ahriman.core.module_loader import implementations
from ahriman.web.views.base import BaseView


__all__ = ["setup_routes"]


def _dynamic_routes(configuration: Configuration) -> Iterator[tuple[str, type[View]]]:
    """
    extract dynamic routes based on views

    Args:
        configuration(Configuration): configuration instance

    Yields:
        tuple[str, type[View]]: map of the route to its view
    """
    for view in implementations(ahriman.web.views, BaseView):
        for route in view.routes(configuration):
            yield route, view


def _identifier(route: str) -> str:
    """
    extract valid route identifier (aka name) for the route. This method replaces curly brackets by single colon
    and replaces other special symbols (including slashes) by underscore

    Args:
        route(str): source route

    Returns:
        str: route with special symbols being replaced
    """
    # replace special symbols
    alphanum = re.sub(r"[^A-Za-z\d\-{}]", "_", route)
    # finally replace curly brackets
    return alphanum.replace("{", ":").replace("}", "")


def setup_routes(application: Application, configuration: Configuration) -> None:
    """
    setup all defined routes

    Args:
        application(Application): web application instance
        configuration(Configuration): configuration instance
    """
    application.router.add_static("/static", configuration.getpath("web", "static_path"),
                                  name="_static", follow_symlinks=True)

    for route, view in _dynamic_routes(configuration):
        application.router.add_view(route, view, name=_identifier(route))
