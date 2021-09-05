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
import tempfile

from pathlib import Path

from ahriman import version
from ahriman.application import handlers
from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.sign_settings import SignSettings


# pylint thinks it is bad idea, but get the fuck off
from ahriman.models.user_access import UserAccess

SubParserAction = argparse._SubParsersAction  # pylint: disable=protected-access


def _parser() -> argparse.ArgumentParser:
    """
    command line parser generator
    :return: command line parser for the application
    """
    parser = argparse.ArgumentParser(prog="ahriman", description="ArcHlinux ReposItory MANager",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-a", "--architecture", help="target architectures (can be used multiple times)",
                        action="append")
    parser.add_argument("-c", "--configuration", help="configuration path", type=Path, default=Path("/etc/ahriman.ini"))
    parser.add_argument("--force", help="force run, remove file lock", action="store_true")
    parser.add_argument(
        "-l",
        "--lock",
        help="lock file",
        type=Path,
        default=Path(tempfile.gettempdir()) / "ahriman.lock")
    parser.add_argument("--no-log", help="redirect all log messages to stderr", action="store_true")
    parser.add_argument("--no-report", help="force disable reporting to web service", action="store_true")
    parser.add_argument("--unsafe", help="allow to run ahriman as non-ahriman user", action="store_true")
    parser.add_argument("-v", "--version", action="version", version=version.__version__)

    subparsers = parser.add_subparsers(title="command", help="command to run", dest="command", required=True)

    _set_add_parser(subparsers)
    _set_check_parser(subparsers)
    _set_clean_parser(subparsers)
    _set_config_parser(subparsers)
    _set_create_user_parser(subparsers)
    _set_init_parser(subparsers)
    _set_key_import_parser(subparsers)
    _set_rebuild_parser(subparsers)
    _set_remove_parser(subparsers)
    _set_remove_unknown_parser(subparsers)
    _set_report_parser(subparsers)
    _set_search_parser(subparsers)
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
    parser = root.add_parser("add", help="add package", description="add package",
                             formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("package", help="package base/name or archive path", nargs="+")
    parser.add_argument("--now", help="run update function after", action="store_true")
    parser.add_argument("--without-dependencies", help="do not add dependencies", action="store_true")
    parser.set_defaults(handler=handlers.Add, architecture=[])
    return parser


def _set_check_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for check subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("check", help="check for updates",
                             description="check for updates. Same as update --dry-run --no-manual",
                             formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("package", help="filter check by package base", nargs="*")
    parser.add_argument("--no-vcs", help="do not check VCS packages", action="store_true")
    parser.set_defaults(handler=handlers.Update, architecture=[], no_aur=False, no_manual=True, dry_run=True)
    return parser


def _set_clean_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for clean subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("clean", help="clean local caches", description="clear local caches",
                             formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--no-build", help="do not clear directory with package sources", action="store_true")
    parser.add_argument("--no-cache", help="do not clear directory with package caches", action="store_true")
    parser.add_argument("--no-chroot", help="do not clear build chroot", action="store_true")
    parser.add_argument("--no-manual", help="do not clear directory with manually added packages", action="store_true")
    parser.add_argument("--no-packages", help="do not clear directory with built packages", action="store_true")
    parser.set_defaults(handler=handlers.Clean, architecture=[], no_log=True, unsafe=True)
    return parser


def _set_config_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for config subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("config", help="dump configuration",
                             description="dump configuration for specified architecture",
                             formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.set_defaults(handler=handlers.Dump, lock=None, no_log=True, no_report=True, unsafe=True)
    return parser


def _set_create_user_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for create user subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser(
        "create-user",
        help="create user for web services",
        description="create user for web services with password and role. In case if password was not entered it will be asked interactively",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("username", help="username for web service")
    parser.add_argument("--as-service", help="add user as service user", action="store_true")
    parser.add_argument("-r", "--role", help="user role", type=UserAccess, choices=UserAccess, default=UserAccess.Read)
    parser.add_argument("-p", "--password", help="user password")
    parser.set_defaults(
        handler=handlers.CreateUser,
        architecture=[""],
        lock=None,
        no_log=True,
        no_report=True,
        unsafe=True)
    return parser


def _set_init_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for init subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("init", help="create repository tree",
                             description="create empty repository tree. Optional command for auto architecture support",
                             formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.set_defaults(handler=handlers.Init, no_report=True)
    return parser


def _set_key_import_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for key import subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("key-import", help="import PGP key",
                             description="import PGP key from public sources to repository user",
                             formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--key-server", help="key server for key import", default="pgp.mit.edu")
    parser.add_argument("key", help="PGP key to import from public server")
    parser.set_defaults(handler=handlers.KeyImport, architecture=[""], lock=None, no_report=True)
    return parser


def _set_rebuild_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for rebuild subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("rebuild", help="rebuild repository", description="rebuild whole repository",
                             formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--depends-on", help="only rebuild packages that depend on specified package", action="append")
    parser.set_defaults(handler=handlers.Rebuild, architecture=[])
    return parser


def _set_remove_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for remove subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("remove", help="remove package", description="remove package",
                             formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("package", help="package name or base", nargs="+")
    parser.set_defaults(handler=handlers.Remove, architecture=[])
    return parser


def _set_remove_unknown_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for remove unknown packages subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("remove-unknown", help="remove unknown packages",
                             description="remove packages which are missing in AUR",
                             formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--dry-run", help="just perform check for packages without removal", action="store_true")
    parser.set_defaults(handler=handlers.RemoveUnknown, architecture=[])
    return parser


def _set_report_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for report subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("report", help="generate report", description="generate report",
                             formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("target", help="target to generate report", nargs="*")
    parser.set_defaults(handler=handlers.Report, architecture=[])
    return parser


def _set_search_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for search subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("search", help="search for package", description="search for package in AUR using API")
    parser.add_argument("search", help="search terms, can be specified multiple times", nargs="+")
    parser.set_defaults(handler=handlers.Search, architecture=[""], lock=None, no_log=True, no_report=True, unsafe=True)
    return parser


def _set_setup_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for setup subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("setup", help="initial service configuration",
                             description="create initial service configuration, requires root",
                             formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--build-command", help="build command prefix", default="ahriman")
    parser.add_argument("--from-configuration", help="path to default devtools pacman configuration",
                        type=Path, default=Path("/usr/share/devtools/pacman-extra.conf"))
    parser.add_argument("--no-multilib", help="do not add multilib repository", action="store_true")
    parser.add_argument("--packager", help="packager name and email", required=True)
    parser.add_argument("--repository", help="repository name", required=True)
    parser.add_argument("--sign-key", help="sign key id")
    parser.add_argument("--sign-target", help="sign options", type=SignSettings.from_option,
                        choices=SignSettings, action="append")
    parser.add_argument("--web-port", help="port of the web service", type=int)
    parser.set_defaults(handler=handlers.Setup, lock=None, no_log=True, no_report=True, unsafe=True)
    return parser


def _set_sign_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for sign subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("sign", help="sign packages", description="(re-)sign packages and repository database",
                             formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("package", help="sign only specified packages", nargs="*")
    parser.set_defaults(handler=handlers.Sign, architecture=[])
    return parser


def _set_status_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for status subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("status", help="get package status", description="request status of the package",
                             formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--ahriman", help="get service status itself", action="store_true")
    parser.add_argument("package", help="filter status by package base", nargs="*")
    parser.set_defaults(handler=handlers.Status, lock=None, no_log=True, no_report=True, unsafe=True)
    return parser


def _set_status_update_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for status update subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("status-update", help="update package status", description="request status of the package",
                             formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "package",
        help="set status for specified packages. If no packages supplied, service status will be updated",
        nargs="*")
    parser.add_argument("--status", help="new status", choices=BuildStatusEnum,
                        type=BuildStatusEnum, default=BuildStatusEnum.Success)
    parser.add_argument("--remove", help="remove package status page", action="store_true")
    parser.set_defaults(handler=handlers.StatusUpdate, lock=None, no_log=True, no_report=True, unsafe=True)
    return parser


def _set_sync_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for sync subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("sync", help="sync repository", description="sync packages to remote server",
                             formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("target", help="target to sync", nargs="*")
    parser.set_defaults(handler=handlers.Sync, architecture=[])
    return parser


def _set_update_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for update subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("update", help="update packages", description="run updates",
                             formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("package", help="filter check by package base", nargs="*")
    parser.add_argument("--dry-run", help="just perform check for updates, same as check command", action="store_true")
    parser.add_argument("--no-aur", help="do not check for AUR updates. Implies --no-vcs", action="store_true")
    parser.add_argument("--no-manual", help="do not include manual updates", action="store_true")
    parser.add_argument("--no-vcs", help="do not check VCS packages", action="store_true")
    parser.set_defaults(handler=handlers.Update, architecture=[])
    return parser


def _set_web_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for web subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("web", help="start web server", description="start web server",
                             formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.set_defaults(handler=handlers.Web, lock=None, no_report=True)
    return parser


def run() -> None:
    """
    run application instance
    """
    if __name__ == "__main__":
        args_parser = _parser()
        args = args_parser.parse_args()

        handler: handlers.Handler = args.handler
        status = handler.execute(args)

        sys.exit(status)


run()
