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
import aiohttp_jinja2  # type: ignore
import jinja2
import logging

from aiohttp import web

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import InitializeException
from ahriman.core.watcher.watcher import Watcher
from ahriman.web.middlewares.exception_handler import exception_handler
from ahriman.web.routes import setup_routes


async def on_shutdown(application: web.Application) -> None:
    '''
    web application shutdown handler
    :param application: web application instance
    '''
    application.logger.warning('server terminated')


async def on_startup(application: web.Application) -> None:
    '''
    web application start handler
    :param application: web application instance
    '''
    application.logger.info('server started')
    try:
        application['watcher'].load()
    except Exception:
        application.logger.exception('could not load packages', exc_info=True)
        raise InitializeException()


def run_server(application: web.Application, architecture: str) -> None:
    '''
    run web application
    :param application: web application instance
    :param architecture: repository architecture
    '''
    application.logger.info('start server')

    section = application['config'].get_section_name('web', architecture)
    host = application['config'].get(section, 'host')
    port = application['config'].getint(section, 'port')

    web.run_app(application, host=host, port=port, handle_signals=False,
                access_log=logging.getLogger('http'))


def setup_service(architecture: str, config: Configuration) -> web.Application:
    '''
    create web application
    :param architecture: repository architecture
    :param config: configuration instance
    :return: web application instance
    '''
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
