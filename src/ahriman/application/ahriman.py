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

from ahriman.models.build_status import BuildStatusEnum


# pylint thinks it is bad idea, but get the fuck off
# pylint: disable=protected-access
SubParserAction = argparse._SubParsersAction


def _parser() -> argparse.ArgumentParser:
    """
    command line parser generator
    :return: command line parser for the application
    """
    parser = argparse.ArgumentParser(prog="ahriman", description="ArcHlinux ReposItory MANager")
    parser.add_argument("-a", "--architecture", help="target architectures (can be used multiple times)",
                        action="append", required=True)
    parser.add_argument("-c", "--config", help="configuration path", default="/etc/ahriman.ini")
    parser.add_argument("--force", help="force run, remove file lock", action="store_true")
    parser.add_argument("--lock", help="lock file", default="/tmp/ahriman.lock")
    parser.add_argument("--no-log", help="redirect all log messages to stderr", action="store_true")
    parser.add_argument("--no-report", help="force disable reporting to web service", action="store_true")
    parser.add_argument("--unsafe", help="allow to run ahriman as non-ahriman user", action="store_true")
    parser.add_argument("-v", "--version", action="version", version=version.__version__)

    subparsers = parser.add_subparsers(title="command", help="command to run", dest="command", required=True)

    _set_add_parser(subparsers)
    _set_check_parser(subparsers)
    _set_clean_parser(subparsers)
    _set_config_parser(subparsers)
    _set_rebuild_parser(subparsers)
    _set_remove_parser(subparsers)
    _set_report_parser(subparsers)
    _set_setup_parser(subparsers)
    _set_sign_parser(subparsers)
    _set_status_parser(subparsers)
    _set_status_update_parser(subparsers)
    _set_sync_parser(subparsers)
    _set_update_parser(subparsers)
    _set_web_parser(subparsers)

    return parser


def _set_add_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for add subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("add", description="add package")
    parser.add_argument("package", help="package base/name or archive path", nargs="+")
    parser.add_argument("--without-dependencies", help="do not add dependencies", action="store_true")
    parser.set_defaults(handler=handlers.Add)
    return parser


def _set_check_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for check subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("check", description="check for updates. Same as update --dry-run --no-manual")
    parser.add_argument("package", help="filter check by package base", nargs="*")
    parser.add_argument("--no-vcs", help="do not check VCS packages", action="store_true")
    parser.set_defaults(handler=handlers.Update, no_aur=False, no_manual=True, dry_run=True)
    return parser


def _set_clean_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for clean subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("clean", description="clear all local caches")
    parser.add_argument("--no-build", help="do not clear directory with package sources", action="store_true")
    parser.add_argument("--no-cache", help="do not clear directory with package caches", action="store_true")
    parser.add_argument("--no-chroot", help="do not clear build chroot", action="store_true")
    parser.add_argument("--no-manual", help="do not clear directory with manually added packages", action="store_true")
    parser.add_argument("--no-packages", help="do not clear directory with built packages", action="store_true")
    parser.set_defaults(handler=handlers.Clean, unsafe=True)
    return parser


def _set_config_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for config subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("config", description="dump configuration for specified architecture")
    parser.set_defaults(handler=handlers.Dump, lock=None, no_report=True, unsafe=True)
    return parser


def _set_rebuild_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for rebuild subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("rebuild", description="rebuild whole repository")
    parser.set_defaults(handler=handlers.Rebuild)
    return parser


def _set_remove_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for remove subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("remove", description="remove package")
    parser.add_argument("package", help="package name or base", nargs="+")
    parser.set_defaults(handler=handlers.Remove)
    return parser


def _set_report_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for report subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("report", description="generate report")
    parser.add_argument("target", help="target to generate report", nargs="*")
    parser.set_defaults(handler=handlers.Report)
    return parser


def _set_setup_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for setup subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("setup", description="create initial service configuration, requires root")
    parser.add_argument("--build-command", help="build command prefix", default="ahriman")
    parser.add_argument("--from-config", help="path to default devtools pacman configuration",
                        default="/usr/share/devtools/pacman-extra.conf")
    parser.add_argument("--no-multilib", help="do not add multilib repository", action="store_true")
    parser.add_argument("--packager", help="packager name and email", required=True)
    parser.add_argument("--repository", help="repository name", default="aur-clone")
    parser.set_defaults(handler=handlers.Setup, lock=None, no_report=True, unsafe=True)
    return parser


def _set_sign_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for sign subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("sign", description="(re-)sign packages and repository database")
    parser.add_argument("package", help="sign only specified packages", nargs="*")
    parser.set_defaults(handler=handlers.Sign)
    return parser


def _set_status_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for status subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("status", description="request status of the package")
    parser.add_argument("--ahriman", help="get service status itself", action="store_true")
    parser.add_argument("package", help="filter status by package base", nargs="*")
    parser.set_defaults(handler=handlers.Status, lock=None, no_report=True, unsafe=True)
    return parser


def _set_status_update_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for status update subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("status-update", description="request status of the package")
    parser.add_argument(
        "package",
        help="set status for specified packages. If no packages supplied, service status will be updated",
        nargs="*")
    parser.add_argument("--status", help="new status", choices=[value.value for value in BuildStatusEnum],
                        default="success")
    parser.set_defaults(handler=handlers.StatusUpdate, lock=None, no_report=True, unsafe=True)
    return parser


def _set_sync_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for sync subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("sync", description="sync packages to remote server")
    parser.add_argument("target", help="target to sync", nargs="*")
    parser.set_defaults(handler=handlers.Sync)
    return parser


def _set_update_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for update subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("update", description="run updates")
    parser.add_argument("package", help="filter check by package base", nargs="*")
    parser.add_argument("--dry-run", help="just perform check for updates, same as check command", action="store_true")
    parser.add_argument("--no-aur", help="do not check for AUR updates. Implies --no-vcs", action="store_true")
    parser.add_argument("--no-manual", help="do not include manual updates", action="store_true")
    parser.add_argument("--no-vcs", help="do not check VCS packages", action="store_true")
    parser.set_defaults(handler=handlers.Update)
    return parser


def _set_web_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for web subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("web", description="start web server")
    parser.set_defaults(handler=handlers.Web, lock=None, no_report=True)
    return parser


if __name__ == "__main__":
    args_parser = _parser()
    args = args_parser.parse_args()

    handler: handlers.Handler = args.handler
    status = handler.execute(args)

    sys.exit(status)
