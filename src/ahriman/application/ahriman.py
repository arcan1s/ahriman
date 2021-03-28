#
# Copyright (c) 2021 ahriman team.
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
import sys

import ahriman.application.handlers as handlers
import ahriman.version as version


# pylint: disable=too-many-statements
def _parser() -> argparse.ArgumentParser:
    """
    command line parser generator
    :return: command line parser for the application
    """
    parser = argparse.ArgumentParser(prog="ahriman", description="ArcHlinux ReposItory MANager")
    parser.add_argument(
        "-a",
        "--architecture",
        help="target architectures (can be used multiple times)",
        action="append",
        required=True)
    parser.add_argument("-c", "--config", help="configuration path", default="/etc/ahriman.ini")
    parser.add_argument("--force", help="force run, remove file lock", action="store_true")
    parser.add_argument("--lock", help="lock file", default="/tmp/ahriman.lock")
    parser.add_argument("--no-log", help="redirect all log messages to stderr", action="store_true")
    parser.add_argument("--no-report", help="force disable reporting to web service", action="store_true")
    parser.add_argument("--unsafe", help="allow to run ahriman as non-ahriman user", action="store_true")
    parser.add_argument("-v", "--version", action="version", version=version.__version__)
    subparsers = parser.add_subparsers(title="command", help="command to run", dest="command", required=True)

    add_parser = subparsers.add_parser("add", description="add package")
    add_parser.add_argument("package", help="package base/name or archive path", nargs="+")
    add_parser.add_argument("--without-dependencies", help="do not add dependencies", action="store_true")
    add_parser.set_defaults(handler=handlers.Add)

    check_parser = subparsers.add_parser("check", description="check for updates. Same as update --dry-run --no-manual")
    check_parser.add_argument("package", help="filter check by package base", nargs="*")
    check_parser.add_argument("--no-vcs", help="do not check VCS packages", action="store_true")
    check_parser.set_defaults(handler=handlers.Update, no_aur=False, no_manual=True, dry_run=True)

    clean_parser = subparsers.add_parser("clean", description="clear all local caches")
    clean_parser.add_argument("--no-build", help="do not clear directory with package sources", action="store_true")
    clean_parser.add_argument("--no-cache", help="do not clear directory with package caches", action="store_true")
    clean_parser.add_argument("--no-chroot", help="do not clear build chroot", action="store_true")
    clean_parser.add_argument(
        "--no-manual",
        help="do not clear directory with manually added packages",
        action="store_true")
    clean_parser.add_argument("--no-packages", help="do not clear directory with built packages", action="store_true")
    clean_parser.set_defaults(handler=handlers.Clean)

    config_parser = subparsers.add_parser("config", description="dump configuration for specified architecture")
    config_parser.set_defaults(handler=handlers.Dump, lock=None, no_report=True, unsafe=True)

    rebuild_parser = subparsers.add_parser("rebuild", description="rebuild whole repository")
    rebuild_parser.set_defaults(handler=handlers.Rebuild)

    remove_parser = subparsers.add_parser("remove", description="remove package")
    remove_parser.add_argument("package", help="package name or base", nargs="+")
    remove_parser.set_defaults(handler=handlers.Remove)

    report_parser = subparsers.add_parser("report", description="generate report")
    report_parser.add_argument("target", help="target to generate report", nargs="*")
    report_parser.set_defaults(handler=handlers.Report)

    status_parser = subparsers.add_parser("status", description="request status of the package")
    status_parser.add_argument("--ahriman", help="get service status itself", action="store_true")
    status_parser.add_argument("package", help="filter status by package base", nargs="*")
    status_parser.set_defaults(handler=handlers.Status, lock=None, no_report=True, unsafe=True)

    sync_parser = subparsers.add_parser("sync", description="sync packages to remote server")
    sync_parser.add_argument("target", help="target to sync", nargs="*")
    sync_parser.set_defaults(handler=handlers.Sync)

    update_parser = subparsers.add_parser("update", description="run updates")
    update_parser.add_argument("package", help="filter check by package base", nargs="*")
    update_parser.add_argument(
        "--dry-run", help="just perform check for updates, same as check command", action="store_true")
    update_parser.add_argument("--no-aur", help="do not check for AUR updates. Implies --no-vcs", action="store_true")
    update_parser.add_argument("--no-manual", help="do not include manual updates", action="store_true")
    update_parser.add_argument("--no-vcs", help="do not check VCS packages", action="store_true")
    update_parser.set_defaults(handler=handlers.Update)

    web_parser = subparsers.add_parser("web", description="start web server")
    web_parser.set_defaults(handler=handlers.Web, lock=None, no_report=True)

    return parser


if __name__ == "__main__":
    arg_parser = _parser()
    args = arg_parser.parse_args()

    handler: handlers.Handler = args.handler
    status = handler.execute(args)

    sys.exit(status)
