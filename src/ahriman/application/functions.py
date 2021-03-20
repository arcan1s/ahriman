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

from typing import Iterable, Tuple

from ahriman.application.application import Application
from ahriman.core.configuration import Configuration
from ahriman.models.build_status import BuildStatus
from ahriman.models.package import Package


def add(args: argparse.Namespace, architecture: str, config: Configuration) -> None:
    '''
    add packages callback
    :param args: command line args
    :param architecture: repository architecture
    :param config: configuration instance
    '''
    Application(architecture, config).add(args.package, args.without_dependencies)


def clean(args: argparse.Namespace, architecture: str, config: Configuration) -> None:
    '''
    clean caches callback
    :param args: command line args
    :param architecture: repository architecture
    :param config: configuration instance
    '''
    Application(architecture, config).clean(args.no_build, args.no_cache, args.no_chroot,
                                            args.no_manual, args.no_packages)


def dump_config(args: argparse.Namespace, architecture: str, config: Configuration) -> None:
    '''
    configuration dump callback
    :param args: command line args
    :param architecture: repository architecture
    :param config: configuration instance
    '''
    del args
    config_dump = config.dump(architecture)
    for section, values in sorted(config_dump.items()):
        print(f'[{section}]')
        for key, value in sorted(values.items()):
            print(f'{key} = {value}')
        print()


def rebuild(args: argparse.Namespace, architecture: str, config: Configuration) -> None:
    '''
    world rebuild callback
    :param args: command line args
    :param architecture: repository architecture
    :param config: configuration instance
    '''
    del args
    app = Application(architecture, config)
    packages = app.repository.packages()
    app.update(packages)


def remove(args: argparse.Namespace, architecture: str, config: Configuration) -> None:
    '''
    remove packages callback
    :param args: command line args
    :param architecture: repository architecture
    :param config: configuration instance
    '''
    Application(architecture, config).remove(args.package)


def report(args: argparse.Namespace, architecture: str, config: Configuration) -> None:
    '''
    generate report callback
    :param args: command line args
    :param architecture: repository architecture
    :param config: configuration instance
    '''
    Application(architecture, config).report(args.target)


def status(args: argparse.Namespace, architecture: str, config: Configuration) -> None:
    '''
    package status callback
    :param args: command line args
    :param architecture: repository architecture
    :param config: configuration instance
    '''
    application = Application(architecture, config)
    if args.ahriman:
        ahriman = application.repository.reporter.get_self()
        print(ahriman.pretty_print())
        print()
    if args.package:
        packages: Iterable[Tuple[Package, BuildStatus]] = sum(
            [application.repository.reporter.get(base) for base in args.package],
            start=[])
    else:
        packages = application.repository.reporter.get(None)
    for package, package_status in sorted(packages, key=lambda item: item[0].base):
        print(package.pretty_print())
        print(f'\t{package.version}')
        print(f'\t{package_status.pretty_print()}')


def sync(args: argparse.Namespace, architecture: str, config: Configuration) -> None:
    '''
    sync to remote server callback
    :param args: command line args
    :param architecture: repository architecture
    :param config: configuration instance
    '''
    Application(architecture, config).sync(args.target)


def update(args: argparse.Namespace, architecture: str, config: Configuration) -> None:
    '''
    update packages callback
    :param args: command line args
    :param architecture: repository architecture
    :param config: configuration instance
    '''
    # typing workaround
    def log_fn(line: str) -> None:
        return print(line) if args.dry_run else application.logger.info(line)

    application = Application(architecture, config)
    packages = application.get_updates(args.package, args.no_aur, args.no_manual, args.no_vcs, log_fn)
    if args.dry_run:
        return

    application.update(packages)


def web(args: argparse.Namespace, architecture: str, config: Configuration) -> None:
    '''
    web server callback
    :param args: command line args
    :param architecture: repository architecture
    :param config: configuration instance
    '''
    del args
    from ahriman.web.web import run_server, setup_service
    application = setup_service(architecture, config)
    run_server(application, architecture)
