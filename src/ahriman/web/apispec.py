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
import aiohttp_apispec  # type: ignore[import]

from aiohttp.web import Application
from typing import Any

from ahriman import version
from ahriman.core.configuration import Configuration


__all__ = ["setup_apispec"]


def _info() -> dict[str, Any]:
    """
    create info object for swagger docs

    Returns:
        dict[str, Any]: info object as per openapi specification
    """
    return {
        "title": "ahriman",
        "description": """Wrapper for managing custom repository inspired by [repo-scripts](https://github.com/arcan1s/repo-scripts).

## Features

* Install-configure-forget manager for the very own repository.
* Multi-architecture support.
* Dependency manager.
* VCS packages support.
* Official repository support.
* Ability to patch AUR packages and even create package from local PKGBUILDs.
* Sign support with gpg (repository, package, per package settings).
* Triggers for repository updates, e.g. synchronization to remote services (rsync, s3 and github) and report generation (email, html, telegram).
* Repository status interface with optional authorization and control options

<security-definitions />
""",
        "license": {
            "name": "GPL3",
            "url": "https://raw.githubusercontent.com/arcan1s/ahriman/master/COPYING",
        },
        "version": version.__version__,
    }


def _security() -> list[dict[str, Any]]:
    """
    get security definitions

    Returns:
        list[dict[str, Any]]: generated security definition
    """
    return [{
        "token": {
            "type": "apiKey",  # as per specification we are using api key
            "name": "API_SESSION",
            "in": "cookie",
        }
    }]


def _servers(application: Application) -> list[dict[str, Any]]:
    """
    get list of defined addresses for server

    Args:
        application(Application): web application instance

    Returns:
        list[dict[str, Any]]: list (actually only one) of defined web urls
    """
    configuration: Configuration = application["configuration"]
    address = configuration.get("web", "address", fallback=None)
    if not address:
        host = configuration.get("web", "host")
        port = configuration.getint("web", "port")
        address = f"http://{host}:{port}"

    return [{
        "url": address,
    }]


def setup_apispec(application: Application) -> aiohttp_apispec.AiohttpApiSpec:
    """
    setup swagger api specification

    Args:
        application(Application): web application instance

    Returns:
        aiohttp_apispec.AiohttpApiSpec: created specification instance
    """
    return aiohttp_apispec.setup_aiohttp_apispec(
        application,
        url="/api-docs/swagger.json",
        openapi_version="3.0.2",
        info=_info(),
        servers=_servers(application),
        security=_security(),
    )
