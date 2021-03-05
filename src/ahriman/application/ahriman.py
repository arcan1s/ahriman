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
import argparse
import os
import shutil

import ahriman.version as version

from ahriman.application.application import Application
from ahriman.core.configuration import Configuration


def _get_app(args: argparse.Namespace) -> Application:
    config = _get_config(args.config)
    return Application(config)


def _get_config(config_path: str) -> Configuration:
    config = Configuration()
    config.load(config_path)
    config.load_logging()
    return config


def _remove_lock(path: str) -> None:
    shutil.rmtree(path, ignore_errors=True)


def add(args: argparse.Namespace) -> None:
    _get_app(args).add(args.package)


def remove(args: argparse.Namespace) -> None:
    _get_app(args).remove(args.package)


def sync(args: argparse.Namespace) -> None:
    _get_app(args).sync()


def update(args: argparse.Namespace) -> None:
    _get_app(args).update(args.sync)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ArcHlinux ReposItory MANager')
    parser.add_argument('-c', '--config', help='configuration path', default='/etc/ahriman.ini')
    parser.add_argument('--force', help='force run, remove file lock', action='store_true')
    parser.add_argument('--lock', help='lock file', default='/tmp/ahriman.lock')
    parser.add_argument('-v', '--version', action='version', version=version.__version__)
    subparsers = parser.add_subparsers(title='commands')

    add_parser = subparsers.add_parser('add', description='add package')
    add_parser.add_argument('package', help='package name', nargs='+')
    add_parser.set_defaults(fn=add)

    remove_parser = subparsers.add_parser('remove', description='remove package')
    remove_parser.add_argument('package', help='package name', nargs='+')
    remove_parser.set_defaults(fn=remove)

    sync_parser = subparsers.add_parser('sync', description='sync packages to remote server')
    sync_parser.set_defaults(fn=sync)

    update_parser = subparsers.add_parser('update', description='run updates')
    update_parser.add_argument('-s', '--sync', help='sync packages to remote server', action='store_true')
    update_parser.set_defaults(fn=update)

    args = parser.parse_args()

    if args.force:
        _remove_lock(args.lock)
    if os.path.exists(args.lock):
        raise RuntimeError('Another application instance is run')

    if 'fn' not in args:
        parser.print_help()
        exit(1)

    try:
        open(args.lock, 'w').close()
        args.fn(args)
    finally:
        _remove_lock(args.lock)

