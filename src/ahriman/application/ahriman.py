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
from typing import TypeVar

from ahriman import version
from ahriman.application import handlers
from ahriman.models.action import Action
from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.package_source import PackageSource
from ahriman.models.sign_settings import SignSettings
from ahriman.models.user_access import UserAccess


# this workaround is for several things
# firstly python devs don't think that is it error and asking you for workarounds https://bugs.python.org/issue41592
# secondly linters don't like when you are importing private members
# thirdly new mypy doesn't like _SubParsersAction and thinks it is a template
SubParserAction = TypeVar("SubParserAction", bound="argparse._SubParsersAction[argparse.ArgumentParser]")


def _formatter(prog: str) -> argparse.HelpFormatter:
    """
    formatter for the help message
    :param prog: application name
    :return: formatter used by default
    """
    return argparse.ArgumentDefaultsHelpFormatter(prog, width=120)


def _parser() -> argparse.ArgumentParser:
    """
    command line parser generator
    :return: command line parser for the application
    """
    parser = argparse.ArgumentParser(prog="ahriman", description="ArcH Linux ReposItory MANager",
                                     epilog="Argument list can also be read from file by using @ prefix.",
                                     fromfile_prefix_chars="@", formatter_class=_formatter)
    parser.add_argument("-a", "--architecture", help="target architectures (can be used multiple times)",
                        action="append")
    parser.add_argument("-c", "--configuration", help="configuration path", type=Path, default=Path("/etc/ahriman.ini"))
    parser.add_argument("--force", help="force run, remove file lock", action="store_true")
    parser.add_argument("-l", "--lock", help="lock file", type=Path,
                        default=Path(tempfile.gettempdir()) / "ahriman.lock")
    parser.add_argument("--no-report", help="force disable reporting to web service", action="store_true")
    parser.add_argument("-q", "--quiet", help="force disable any logging", action="store_true")
    parser.add_argument("--unsafe", help="allow to run ahriman as non-ahriman user. Some actions might be unavailable",
                        action="store_true")
    parser.add_argument("-v", "--version", action="version", version=version.__version__)

    subparsers = parser.add_subparsers(title="command", help="command to run", dest="command", required=True)

    _set_aur_search_parser(subparsers)
    _set_key_import_parser(subparsers)
    _set_package_add_parser(subparsers)
    _set_package_remove_parser(subparsers)
    _set_package_status_parser(subparsers)
    _set_package_status_remove_parser(subparsers)
    _set_package_status_update_parser(subparsers)
    _set_patch_add_parser(subparsers)
    _set_patch_list_parser(subparsers)
    _set_patch_remove_parser(subparsers)
    _set_repo_check_parser(subparsers)
    _set_repo_clean_parser(subparsers)
    _set_repo_config_parser(subparsers)
    _set_repo_init_parser(subparsers)
    _set_repo_rebuild_parser(subparsers)
    _set_repo_remove_unknown_parser(subparsers)
    _set_repo_report_parser(subparsers)
    _set_repo_setup_parser(subparsers)
    _set_repo_sign_parser(subparsers)
    _set_repo_status_update_parser(subparsers)
    _set_repo_sync_parser(subparsers)
    _set_repo_update_parser(subparsers)
    _set_user_add_parser(subparsers)
    _set_user_remove_parser(subparsers)
    _set_web_parser(subparsers)

    return parser


def _set_aur_search_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for AUR search subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("aur-search", aliases=["search"], help="search for package",
                             description="search for package in AUR using API", formatter_class=_formatter)
    parser.add_argument("search", help="search terms, can be specified multiple times, result will match all terms",
                        nargs="+")
    parser.add_argument("-i", "--info", help="show additional package information", action="store_true")
    parser.add_argument("--sort-by", help="sort field by this field. In case if two packages have the same value of "
                                          "the specified field, they will be always sorted by name",
                        default="name", choices=sorted(handlers.Search.SORT_FIELDS))
    parser.set_defaults(handler=handlers.Search, architecture=[""], lock=None, no_report=True, quiet=True, unsafe=True)
    return parser


def _set_key_import_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for key import subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("key-import", help="import PGP key",
                             description="import PGP key from public sources to the repository user",
                             epilog="By default ahriman runs build process with package sources validation "
                                    "(in case if signature and keys are available in PKGBUILD). This process will "
                                    "fail in case if key is not known for build user. This subcommand can be used "
                                    "in order to import the PGP key to user keychain.",
                             formatter_class=_formatter)
    parser.add_argument("--key-server", help="key server for key import", default="pgp.mit.edu")
    parser.add_argument("key", help="PGP key to import from public server")
    parser.set_defaults(handler=handlers.KeyImport, architecture=[""], lock=None, no_report=True)
    return parser


def _set_package_add_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for package addition subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("package-add", aliases=["add", "package-update"], help="add package",
                             description="add existing or new package to the build queue",
                             epilog="This subcommand should be used for new package addition. It also supports flag "
                                    "--now in case if you would like to build the package immediately. "
                                    "You can add new package from one of supported sources: "
                                    "1) if it is already built package you can specify the path to the archive; "
                                    "2) you can also add built packages from the directory (e.g. during the migration "
                                    "from another repository source); "
                                    "3) it is also possible to add package from local PKGBUILD, but in this case it "
                                    "will be ignored during the next automatic updates; "
                                    "4) ahriman supports downloading archives from remote (e.g. HTTP) sources; "
                                    "5) and finally you can add package from AUR.",
                             formatter_class=_formatter)
    parser.add_argument("package", help="package source (base name, path to local files, remote URL)", nargs="+")
    parser.add_argument("-n", "--now", help="run update function after", action="store_true")
    parser.add_argument("-s", "--source", help="explicitly specify the package source for this command",
                        type=PackageSource, choices=PackageSource, default=PackageSource.Auto)
    parser.add_argument("--without-dependencies", help="do not add dependencies", action="store_true")
    parser.set_defaults(handler=handlers.Add)
    return parser


def _set_package_remove_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for package removal subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("package-remove", aliases=["remove"], help="remove package",
                             description="remove package from the repository", formatter_class=_formatter)
    parser.add_argument("package", help="package name or base", nargs="+")
    parser.set_defaults(handler=handlers.Remove)
    return parser


def _set_package_status_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for package status subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("package-status", aliases=["status"], help="get package status",
                             description="request status of the package",
                             epilog="This feature requests package status from the web interface if it is available.",
                             formatter_class=_formatter)
    parser.add_argument("package", help="filter status by package base", nargs="*")
    parser.add_argument("--ahriman", help="get service status itself", action="store_true")
    parser.add_argument("-i", "--info", help="show additional package information", action="store_true")
    parser.add_argument("-s", "--status", help="filter packages by status",
                        type=BuildStatusEnum, choices=BuildStatusEnum)
    parser.set_defaults(handler=handlers.Status, lock=None, no_report=True, quiet=True, unsafe=True)
    return parser


def _set_package_status_remove_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for package status remove subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("package-status-remove", help="remove package status",
                             description="remove the package from the status page",
                             epilog="Please note that this subcommand does not remove the package itself, it just "
                                    "clears the status page.",
                             formatter_class=_formatter)
    parser.add_argument("package", help="remove specified packages", nargs="+")
    parser.set_defaults(handler=handlers.StatusUpdate, action=Action.Remove, lock=None, no_report=True, quiet=True,
                        unsafe=True)
    return parser


def _set_package_status_update_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for package status update subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("package-status-update", aliases=["status-update"], help="update package status",
                             description="update package status on the status page", formatter_class=_formatter)
    parser.add_argument("package", help="set status for specified packages. "
                                        "If no packages supplied, service status will be updated",
                        nargs="*")
    parser.add_argument("-s", "--status", help="new status",
                        type=BuildStatusEnum, choices=BuildStatusEnum, default=BuildStatusEnum.Success)
    parser.set_defaults(handler=handlers.StatusUpdate, action=Action.Update, lock=None, no_report=True, quiet=True,
                        unsafe=True)
    return parser


def _set_patch_add_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for new patch subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("patch-add", help="add patch set", description="create or update source patches",
                             epilog="In order to add a patch set for the package you will need to clone "
                                    "the AUR package manually, add required changes (e.g. external patches, "
                                    "edit PKGBUILD) and run command, e.g. `ahriman patch path/to/directory`. "
                                    "By default it tracks *.patch and *.diff files, but this behavior can be changed "
                                    "by using --track option",
                             formatter_class=_formatter)
    parser.add_argument("package", help="path to directory with changed files for patch addition/update")
    parser.add_argument("-t", "--track", help="files which has to be tracked", action="append",
                        default=["*.diff", "*.patch"])
    parser.set_defaults(handler=handlers.Patch, action=Action.Update, architecture=[""], lock=None, no_report=True)
    return parser


def _set_patch_list_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for list patches subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("patch-list", help="list patch sets",
                             description="list available patches for the package", formatter_class=_formatter)
    parser.add_argument("package", help="package base")
    parser.set_defaults(handler=handlers.Patch, action=Action.List, architecture=[""], lock=None, no_report=True)
    return parser


def _set_patch_remove_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for remove patches subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("patch-remove", help="remove patch set", description="remove patches for the package",
                             formatter_class=_formatter)
    parser.add_argument("package", help="package base")
    parser.set_defaults(handler=handlers.Patch, action=Action.Remove, architecture=[""], lock=None, no_report=True)
    return parser


def _set_repo_check_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for repository check subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("repo-check", aliases=["check"], help="check for updates",
                             description="check for packages updates. Same as update --dry-run --no-manual",
                             formatter_class=_formatter)
    parser.add_argument("package", help="filter check by package base", nargs="*")
    parser.add_argument("--no-vcs", help="do not check VCS packages", action="store_true")
    parser.set_defaults(handler=handlers.Update, dry_run=True, no_aur=False, no_local=False, no_manual=True)
    return parser


def _set_repo_clean_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for repository clean subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("repo-clean", aliases=["clean"], help="clean local caches",
                             description="remove local caches",
                             epilog="The subcommand clears every temporary directories (builds, caches etc). Normally "
                                    "you should not run this command manually. Also in case if you are going to clear "
                                    "the chroot directories you will need root privileges.",
                             formatter_class=_formatter)
    parser.add_argument("--build", help="clear directory with package sources", action="store_true")
    parser.add_argument("--cache", help="clear directory with package caches", action="store_true")
    parser.add_argument("--chroot", help="clear build chroot", action="store_true")
    parser.add_argument("--manual", help="clear directory with manually added packages", action="store_true")
    parser.add_argument("--packages", help="clear directory with built packages", action="store_true")
    parser.add_argument("--patches", help="clear directory with patches", action="store_true")
    parser.set_defaults(handler=handlers.Clean, quiet=True, unsafe=True)
    return parser


def _set_repo_config_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for config subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("repo-config", aliases=["config"], help="dump configuration",
                             description="dump configuration for the specified architecture",
                             formatter_class=_formatter)
    parser.set_defaults(handler=handlers.Dump, lock=None, no_report=True, quiet=True, unsafe=True)
    return parser


def _set_repo_init_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for repository init subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("repo-init", aliases=["init"], help="create repository tree",
                             description="create empty repository tree. Optional command for auto architecture support",
                             formatter_class=_formatter)
    parser.set_defaults(handler=handlers.Init, no_report=True)
    return parser


def _set_repo_rebuild_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for repository rebuild subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("repo-rebuild", aliases=["rebuild"], help="rebuild repository",
                             description="force rebuild whole repository", formatter_class=_formatter)
    parser.add_argument("--depends-on", help="only rebuild packages that depend on specified package", action="append")
    parser.add_argument("--dry-run", help="just perform check for packages without rebuild process itself",
                        action="store_true")
    parser.set_defaults(handler=handlers.Rebuild)
    return parser


def _set_repo_remove_unknown_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for remove unknown packages subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("repo-remove-unknown", aliases=["remove-unknown"], help="remove unknown packages",
                             description="remove packages which are missing in AUR and do not have local PKGBUILDs",
                             formatter_class=_formatter)
    parser.add_argument("--dry-run", help="just perform check for packages without removal", action="store_true")
    parser.add_argument("-i", "--info", help="show additional package information", action="store_true")
    parser.set_defaults(handler=handlers.RemoveUnknown)
    return parser


def _set_repo_report_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for report subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("repo-report", aliases=["report"], help="generate report",
                             description="generate repository report according to current settings",
                             epilog="Create and/or update repository report as configured.",
                             formatter_class=_formatter)
    parser.add_argument("target", help="target to generate report", nargs="*")
    parser.set_defaults(handler=handlers.Report)
    return parser


def _set_repo_setup_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for setup subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("repo-setup", aliases=["setup"], help="initial service configuration",
                             description="create initial service configuration, requires root",
                             epilog="Create _minimal_ configuration for the service according to provided options.",
                             formatter_class=_formatter)
    parser.add_argument("--build-command", help="build command prefix", default="ahriman")
    parser.add_argument("--from-configuration", help="path to default devtools pacman configuration",
                        type=Path, default=Path("/usr/share/devtools/pacman-extra.conf"))
    parser.add_argument("--no-multilib", help="do not add multilib repository", action="store_true")
    parser.add_argument("--packager", help="packager name and email", required=True)
    parser.add_argument("--repository", help="repository name", required=True)
    parser.add_argument("--sign-key", help="sign key id")
    parser.add_argument("--sign-target", help="sign options", action="append",
                        type=SignSettings.from_option, choices=SignSettings)
    parser.add_argument("--web-port", help="port of the web service", type=int)
    parser.set_defaults(handler=handlers.Setup, lock=None, no_report=True, quiet=True, unsafe=True)
    return parser


def _set_repo_sign_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for sign subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("repo-sign", aliases=["sign"], help="sign packages",
                             description="(re-)sign packages and repository database according to current settings",
                             epilog="Sign repository and/or packages as configured.",
                             formatter_class=_formatter)
    parser.add_argument("package", help="sign only specified packages", nargs="*")
    parser.set_defaults(handler=handlers.Sign)
    return parser


def _set_repo_status_update_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for repository status update subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("repo-status-update", help="update repository status",
                             description="update repository status on the status page", formatter_class=_formatter)
    parser.add_argument("-s", "--status", help="new status",
                        type=BuildStatusEnum, choices=BuildStatusEnum, default=BuildStatusEnum.Success)
    parser.set_defaults(handler=handlers.StatusUpdate, action=Action.Update, lock=None, no_report=True, package=[],
                        quiet=True, unsafe=True)
    return parser


def _set_repo_sync_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for repository sync subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("repo-sync", aliases=["sync"], help="sync repository",
                             description="sync repository files to remote server according to current settings",
                             epilog="Synchronize the repository to remote services as configured.",
                             formatter_class=_formatter)
    parser.add_argument("target", help="target to sync", nargs="*")
    parser.set_defaults(handler=handlers.Sync)
    return parser


def _set_repo_update_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for repository update subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("repo-update", aliases=["update"], help="update packages",
                             description="check for packages updates and run build process if requested",
                             formatter_class=_formatter)
    parser.add_argument("package", help="filter check by package base", nargs="*")
    parser.add_argument("--dry-run", help="just perform check for updates, same as check command", action="store_true")
    parser.add_argument("--no-aur", help="do not check for AUR updates. Implies --no-vcs", action="store_true")
    parser.add_argument("--no-local", help="do not check local packages for updates", action="store_true")
    parser.add_argument("--no-manual", help="do not include manual updates", action="store_true")
    parser.add_argument("--no-vcs", help="do not check VCS packages", action="store_true")
    parser.set_defaults(handler=handlers.Update)
    return parser


def _set_user_add_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for create user subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("user-add", help="create or update user",
                             description="update user for web services with the given password and role. "
                                         "In case if password was not entered it will be asked interactively",
                             formatter_class=_formatter)
    parser.add_argument("username", help="username for web service")
    parser.add_argument("--as-service", help="add user as service user", action="store_true")
    parser.add_argument("--no-reload", help="do not reload authentication module", action="store_true")
    parser.add_argument("-p", "--password", help="user password. Blank password will be treated as empty password, "
                                                 "which is in particular must be used for OAuth2 authorization type.")
    parser.add_argument("-r", "--role", help="user access level",
                        type=UserAccess, choices=UserAccess, default=UserAccess.Read)
    parser.add_argument("-s", "--secure", help="set file permissions to user-only", action="store_true")
    parser.set_defaults(handler=handlers.User, action=Action.Update, architecture=[""], lock=None, no_report=True,
                        quiet=True, unsafe=True)
    return parser


def _set_user_remove_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for user removal subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("user-remove", help="remove user",
                             description="remove user from the user mapping and update the configuration",
                             formatter_class=_formatter)
    parser.add_argument("username", help="username for web service")
    parser.add_argument("--no-reload", help="do not reload authentication module", action="store_true")
    parser.add_argument("-s", "--secure", help="set file permissions to user-only", action="store_true")
    parser.set_defaults(handler=handlers.User, action=Action.Remove, architecture=[""], lock=None, no_report=True,  # nosec
                        password="", quiet=True, role=UserAccess.Read, unsafe=True)
    return parser


def _set_web_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for web subcommand
    :param root: subparsers for the commands
    :return: created argument parser
    """
    parser = root.add_parser("web", help="web server", description="start web server", formatter_class=_formatter)
    parser.set_defaults(handler=handlers.Web, lock=None, no_report=True, parser=_parser)
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
