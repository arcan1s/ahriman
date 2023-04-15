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
import aiohttp_jinja2
import jinja2
import logging
import socket

from aiohttp.web import Application, normalize_path_middleware, run_app

from ahriman.core.auth import Auth
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.exceptions import InitializeError
from ahriman.core.log.filtered_access_logger import FilteredAccessLogger
from ahriman.core.spawn import Spawn
from ahriman.core.status.watcher import Watcher
from ahriman.web.apispec import setup_apispec
from ahriman.web.cors import setup_cors
from ahriman.web.middlewares.exception_handler import exception_handler
from ahriman.web.routes import setup_routes


__all__ = ["run_server", "setup_service"]


def _create_socket(configuration: Configuration, application: Application) -> socket.socket | None:
    """
    create unix socket based on configuration option

    Args:
        configuration(Configuration): configuration instance
        application(Application): web application instance

    Returns:
        socket.socket | None: unix socket object if set by option
    """
    unix_socket = configuration.getpath("web", "unix_socket", fallback=None)
    if unix_socket is None:
        return None  # no option set
    # create unix socket and bind it
    unix_socket.unlink(missing_ok=True)  # remove socket file if it wasn't removed somehow before
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(str(unix_socket))
    # allow everyone to write to the socket, otherwise API methods are not allowed by non-ahriman user
    # by default sockets are created with same rights as directory is, but it seems that x bit is not really required
    # see also https://github.com/aio-libs/aiohttp/issues/4155
    if configuration.getboolean("web", "unix_socket_unsafe", fallback=True):
        unix_socket.chmod(0o666)  # for the glory of satan of course

    # register socket removal
    async def remove_socket(_: Application) -> None:
        unix_socket.unlink(missing_ok=True)

    application.on_shutdown.append(remove_socket)

    return sock


async def _on_shutdown(application: Application) -> None:
    """
    web application shutdown handler

    Args:
        application(Application): web application instance
    """
    application.logger.warning("server terminated")


async def _on_startup(application: Application) -> None:
    """
    web application start handler

    Args:
        application(Application): web application instance

    Raises:
        InitializeError: in case if matched could not be loaded
    """
    application.logger.info("server started")
    try:
        application["watcher"].load()
    except Exception:
        message = "could not load packages"
        application.logger.exception(message)
        raise InitializeError(message)


def run_server(application: Application) -> None:
    """
    run web application

    Args:
        application(Application): web application instance
    """
    application.logger.info("start server")

    configuration: Configuration = application["configuration"]
    host = configuration.get("web", "host")
    port = configuration.getint("web", "port")
    unix_socket = _create_socket(configuration, application)

    run_app(application, host=host, port=port, sock=unix_socket, handle_signals=True,
            access_log=logging.getLogger("http"), access_log_class=FilteredAccessLogger)


def setup_service(architecture: str, configuration: Configuration, spawner: Spawn) -> Application:
    """
    create web application

    Args:
        architecture(str): repository architecture
        configuration(Configuration): configuration instance
        spawner(Spawn): spawner thread

    Returns:
        Application: web application instance
    """
    application = Application(logger=logging.getLogger(__name__))
    application.on_shutdown.append(_on_shutdown)
    application.on_startup.append(_on_startup)

    application.middlewares.append(normalize_path_middleware(append_slash=False, remove_slash=True))
    application.middlewares.append(exception_handler(application.logger))

    application.logger.info("setup routes")
    setup_routes(application, configuration.getpath("web", "static_path"))

    application.logger.info("setup CORS")
    setup_cors(application)

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
        import aiohttp_debugtoolbar  # type: ignore[import]
        aiohttp_debugtoolbar.setup(application,
                                   hosts=configuration.getlist("web", "debug_allowed_hosts", fallback=[]),
                                   check_host=configuration.getboolean("web", "debug_check_host", fallback=False))

    application.logger.info("setup authorization")
    validator = application["validator"] = Auth.load(configuration, database)
    if validator.enabled:
        from ahriman.web.middlewares.auth_handler import setup_auth
        setup_auth(application, configuration, validator)

    application.logger.info("setup api docs")
    setup_apispec(application)

    return application
