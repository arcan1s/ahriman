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

import ahriman.version as version

from ahriman.application.application import Application
from ahriman.application.lock import Lock
from ahriman.core.configuration import Configuration


def add(args: argparse.Namespace) -> None:
    '''
    add packages callback
    :param args: command line args
    '''
    Application.from_args(args).add(args.package, args.without_dependencies)


def rebuild(args: argparse.Namespace) -> None:
    '''
    world rebuild callback
    :param args: command line args
    '''
    app = Application.from_args(args)
    packages = app.repository.packages()
    app.update(packages)


def remove(args: argparse.Namespace) -> None:
    '''
    remove packages callback
    :param args: command line args
    '''
    Application.from_args(args).remove(args.package)


def report(args: argparse.Namespace) -> None:
    '''
    generate report callback
    :param args: command line args
    '''
    Application.from_args(args).report(args.target)


def sync(args: argparse.Namespace) -> None:
    '''
    sync to remote server callback
    :param args: command line args
    '''
    Application.from_args(args).sync(args.target)


def update(args: argparse.Namespace) -> None:
    '''
    update packages callback
    :param args: command line args
    '''
    # typing workaround
    def log_fn(line: str) -> None:
        return print(line) if args.dry_run else app.logger.info(line)

    app = Application.from_args(args)
    packages = app.get_updates(args.package, args.no_aur, args.no_manual, args.no_vcs, log_fn)
    if args.dry_run:
        return
    app.update(packages)


def web(args: argparse.Namespace) -> None:
    '''
    web server callback
    :param args: command line args
    '''
    from ahriman.web.web import run_server, setup_service
    config = Configuration.from_path(args.config)
    app = setup_service(args.architecture, config)
    run_server(app, args.architecture)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='ahriman', description='ArcHlinux ReposItory MANager')
    parser.add_argument('-a', '--architecture', help='target architecture', required=True)
    parser.add_argument('-c', '--config', help='configuration path', default='/etc/ahriman.ini')
    parser.add_argument('--force', help='force run, remove file lock', action='store_true')
    parser.add_argument('--lock', help='lock file', default='/tmp/ahriman.lock')
    parser.add_argument('-v', '--version', action='version', version=version.__version__)
    subparsers = parser.add_subparsers(title='command')

    add_parser = subparsers.add_parser('add', description='add package')
    add_parser.add_argument('package', help='package name or archive path', nargs='+')
    add_parser.add_argument('--without-dependencies', help='do not add dependencies', action='store_true')
    add_parser.set_defaults(fn=add)

    check_parser = subparsers.add_parser('check', description='check for updates')
    check_parser.add_argument('package', help='filter check by packages', nargs='*')
    check_parser.set_defaults(fn=update, no_aur=False, no_manual=True, no_vcs=False, dry_run=True)

    rebuild_parser = subparsers.add_parser('rebuild', description='rebuild whole repository')
    rebuild_parser.set_defaults(fn=rebuild)

    remove_parser = subparsers.add_parser('remove', description='remove package')
    remove_parser.add_argument('package', help='package name', nargs='+')
    remove_parser.set_defaults(fn=remove)

    report_parser = subparsers.add_parser('report', description='generate report')
    report_parser.add_argument('target', help='target to generate report', nargs='*')
    report_parser.set_defaults(fn=report)

    sync_parser = subparsers.add_parser('sync', description='sync packages to remote server')
    sync_parser.add_argument('target', help='target to sync', nargs='*')
    sync_parser.set_defaults(fn=sync)

    update_parser = subparsers.add_parser('update', description='run updates')
    update_parser.add_argument('package', help='filter check by packages', nargs='*')
    update_parser.add_argument(
        '--dry-run', help='just perform check for updates, same as check command', action='store_true')
    update_parser.add_argument('--no-aur', help='do not check for AUR updates', action='store_true')
    update_parser.add_argument('--no-manual', help='do not include manual updates', action='store_true')
    update_parser.add_argument('--no-vcs', help='do not check VCS packages', action='store_true')
    update_parser.set_defaults(fn=update)

    web_parser = subparsers.add_parser('web', description='start web server')
    web_parser.set_defaults(fn=web, lock=None)

    args = parser.parse_args()
    if 'fn' not in args:
        parser.print_help()
        exit(1)

    with Lock(args.lock, args.architecture, args.force):
        args.fn(args)
