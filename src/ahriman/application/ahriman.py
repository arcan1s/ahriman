import argparse
import os

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
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def add(args: argparse.Namespace) -> None:
    _get_app(args).add(args.package)


def remove(args: argparse.Namespace) -> None:
    _get_app(args).remove(args.package)


def update(args: argparse.Namespace) -> None:
    _get_app(args).update()


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

    update_parser = subparsers.add_parser('update', description='run updates')
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

