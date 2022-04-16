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
import aiohttp_jinja2
import jinja2
import logging

from aiohttp import web

from ahriman.core.auth.auth import Auth
from ahriman.core.configuration import Configuration
from ahriman.core.database.sqlite import SQLite
from ahriman.core.exceptions import InitializeException
from ahriman.core.spawn import Spawn
from ahriman.core.status.watcher import Watcher
from ahriman.web.middlewares.exception_handler import exception_handler
from ahriman.web.routes import setup_routes


async def on_shutdown(application: web.Application) -> None:
    """
    web application shutdown handler

    Args:
      application(web.Application): web application instance
    """
    application.logger.warning("server terminated")


async def on_startup(application: web.Application) -> None:
    """
    web application start handler

    Args:
      application(web.Application): web application instance
    """
    application.logger.info("server started")
    try:
        application["watcher"].load()
    except Exception:
        message = "could not load packages"
        application.logger.exception(message)
        raise InitializeException(message)


def run_server(application: web.Application) -> None:
    """
    run web application

    Args:
      application(web.Application): web application instance
    """
    application.logger.info("start server")

    configuration: Configuration = application["configuration"]
    host = configuration.get("web", "host")
    port = configuration.getint("web", "port")

    web.run_app(application, host=host, port=port, handle_signals=False,
                access_log=logging.getLogger("http"))


def setup_service(architecture: str, configuration: Configuration, spawner: Spawn) -> web.Application:
    """
    create web application

    Args:
      architecture(str): repository architecture
      configuration(Configuration): configuration instance
      spawner(Spawn): spawner thread

    Returns:
      web.Application: web application instance
    """
    application = web.Application(logger=logging.getLogger("http"))
    application.on_shutdown.append(on_shutdown)
    application.on_startup.append(on_startup)

    application.middlewares.append(web.normalize_path_middleware(append_slash=False, remove_slash=True))
    application.middlewares.append(exception_handler(application.logger))

    application.logger.info("setup routes")
    setup_routes(application, configuration.getpath("web", "static_path"))

    application.logger.info("setup templates")
    aiohttp_jinja2.setup(application, loader=jinja2.FileSystemLoader(configuration.getpath("web", "templates")))

    application.logger.info("setup configuration")
    application["configuration"] = configuration

    application.logger.info("setup database and perform migrations")
    database = application["database"] = SQLite.load(configuration)

    application.logger.info("setup watcher")
    application["watcher"] = Watcher(architecture, configuration, database)

    application.logger.info("setup process spawner")
    application["spawn"] = spawner

    application.logger.info("setup debug panel")
    debug_enabled = configuration.getboolean("web", "debug", fallback=False)
    if debug_enabled:
        import aiohttp_debugtoolbar  # type: ignore
        aiohttp_debugtoolbar.setup(application,
                                   hosts=configuration.getlist("web", "debug_allowed_hosts", fallback=[]),
                                   check_host=configuration.getboolean("web", "debug_check_host", fallback=False))

    application.logger.info("setup authorization")
    validator = application["validator"] = Auth.load(configuration, database)
    if validator.enabled:
        from ahriman.web.middlewares.auth_handler import setup_auth
        setup_auth(application, validator)

    return application
