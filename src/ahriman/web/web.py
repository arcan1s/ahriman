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
import aiohttp_jinja2
import jinja2
import logging

from aiohttp import web

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import InitializeException
from ahriman.core.watcher.watcher import Watcher
from ahriman.web.middlewares.exception_handler import exception_handler
from ahriman.web.routes import setup_routes


async def on_shutdown(app: web.Application) -> None:
    app.logger.warning('server terminated')


async def on_startup(app: web.Application) -> None:
    app.logger.info('server started')
    try:
        app['watcher'].load()
    except Exception as e:
        app.logger.exception('could not load packages', exc_info=True)
        raise InitializeException() from e


def run_server(app: web.Application) -> None:
    app.logger.info('start server')
    web.run_app(app,
                host=app['config'].get('web', 'host'),
                port=app['config'].getint('web', 'port'),
                handle_signals=False)


def setup_service(architecture: str, config: Configuration) -> web.Application:
    app = web.Application(logger=logging.getLogger('http'))
    app.on_shutdown.append(on_shutdown)
    app.on_startup.append(on_startup)

    app.middlewares.append(web.normalize_path_middleware(append_slash=False, remove_slash=True))
    app.middlewares.append(exception_handler(app.logger))

    app.logger.info('setup routes')
    setup_routes(app)
    app.logger.info('setup templates')
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(config.get('web', 'templates')))

    app.logger.info('setup configuration')
    app['config'] = config

    app.logger.info('setup watcher')
    app['watcher'] = Watcher(architecture, config)

    return app
