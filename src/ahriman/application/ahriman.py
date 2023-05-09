#
# Copyright (c) 2021-2023 ahriman team.
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
# pylint: disable=too-many-lines
import argparse
import sys
import tempfile

from pathlib import Path
from typing import TypeVar

from ahriman import version
from ahriman.application import handlers
from ahriman.core.util import enum_values
from ahriman.models.action import Action
from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.package_source import PackageSource
from ahriman.models.sign_settings import SignSettings
from ahriman.models.user_access import UserAccess


__all__: list[str] = []


# this workaround is for several things
# firstly python devs don't think that is it error and asking you for workarounds https://bugs.python.org/issue41592
# secondly linters don't like when you are importing private members
# thirdly new mypy doesn't like _SubParsersAction and thinks it is a template
SubParserAction = TypeVar("SubParserAction", bound="argparse._SubParsersAction[argparse.ArgumentParser]")


def _formatter(prog: str) -> argparse.HelpFormatter:
    """
    formatter for the help message

    Args:
        prog(str): application name

    Returns:
        argparse.HelpFormatter: formatter used by default
    """
    return argparse.ArgumentDefaultsHelpFormatter(prog, width=120)


def _parser() -> argparse.ArgumentParser:
    """
    command line parser generator

    Returns:
        argparse.ArgumentParser: command line parser for the application
    """
    parser = argparse.ArgumentParser(prog="ahriman", description="ArcH linux ReposItory MANager",
                                     epilog="Argument list can also be read from file by using @ prefix.",
                                     fromfile_prefix_chars="@", formatter_class=_formatter)
    parser.add_argument("-a", "--architecture", help="target architectures. For several subcommands it can be used "
                                                     "multiple times", action="append")
    parser.add_argument("-c", "--configuration", help="configuration path", type=Path,
                        default=Path("/etc") / "ahriman.ini")
    parser.add_argument("--force", help="force run, remove file lock", action="store_true")
    parser.add_argument("-l", "--lock", help="lock file", type=Path,
                        default=Path(tempfile.gettempdir()) / "ahriman.lock")
    parser.add_argument("--report", help="force enable or disable reporting to web service",
                        action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("-q", "--quiet", help="force disable any logging", action="store_true")
    parser.add_argument("--unsafe", help="allow to run ahriman as non-ahriman user. Some actions might be unavailable",
                        action="store_true")
    parser.add_argument("-V", "--version", action="version", version=version.__version__)

    subparsers = parser.add_subparsers(title="command", help="command to run", dest="command", required=True)

    _set_aur_search_parser(subparsers)
    _set_help_parser(subparsers)
    _set_help_commands_unsafe_parser(subparsers)
    _set_help_updates_parser(subparsers)
    _set_help_version_parser(subparsers)
    _set_package_add_parser(subparsers)
    _set_package_remove_parser(subparsers)
    _set_package_status_parser(subparsers)
    _set_package_status_remove_parser(subparsers)
    _set_package_status_update_parser(subparsers)
    _set_patch_add_parser(subparsers)
    _set_patch_list_parser(subparsers)
    _set_patch_remove_parser(subparsers)
    _set_patch_set_add_parser(subparsers)
    _set_repo_backup_parser(subparsers)
    _set_repo_check_parser(subparsers)
    _set_repo_daemon_parser(subparsers)
    _set_repo_rebuild_parser(subparsers)
    _set_repo_remove_unknown_parser(subparsers)
    _set_repo_report_parser(subparsers)
    _set_repo_restore_parser(subparsers)
    _set_repo_sign_parser(subparsers)
    _set_repo_status_update_parser(subparsers)
    _set_repo_sync_parser(subparsers)
    _set_repo_tree_parser(subparsers)
    _set_repo_triggers_parser(subparsers)
    _set_repo_update_parser(subparsers)
    _set_service_clean_parser(subparsers)
    _set_service_config_parser(subparsers)
    _set_service_config_validate_parser(subparsers)
    _set_service_key_import_parser(subparsers)
    _set_service_setup_parser(subparsers)
    _set_service_shell_parser(subparsers)
    _set_user_add_parser(subparsers)
    _set_user_list_parser(subparsers)
    _set_user_remove_parser(subparsers)
    _set_web_parser(subparsers)

    return parser


def _set_aur_search_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for AUR search subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("aur-search", aliases=["search"], help="search for package",
                             description="search for package in AUR using API", formatter_class=_formatter)
    parser.add_argument("search", help="search terms, can be specified multiple times, the result will match all terms",
                        nargs="+")
    parser.add_argument("-e", "--exit-code", help="return non-zero exit status if result is empty", action="store_true")
    parser.add_argument("--info", help="show additional package information",
                        action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--sort-by", help="sort field by this field. In case if two packages have the same value of "
                                          "the specified field, they will be always sorted by name",
                        default="name", choices=sorted(handlers.Search.SORT_FIELDS))
    parser.set_defaults(handler=handlers.Search, architecture=[""], lock=None, report=False, quiet=True, unsafe=True)
    return parser


def _set_help_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for listing help subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("help", help="show help message",
                             description="show help message for application or command and exit",
                             formatter_class=_formatter)
    parser.add_argument("command", help="show help message for specific command", nargs="?")
    parser.set_defaults(handler=handlers.Help, architecture=[""], lock=None, report=False, quiet=True, unsafe=True,
                        parser=_parser)
    return parser


def _set_help_commands_unsafe_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for listing unsafe commands

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("help-commands-unsafe", help="list unsafe commands",
                             description="list unsafe commands as defined in default args", formatter_class=_formatter)
    parser.add_argument("--command", help="instead of showing commands, just test command line for unsafe subcommand "
                                          "and return 0 in case if command is safe and 1 otherwise")
    parser.set_defaults(handler=handlers.UnsafeCommands, architecture=[""], lock=None, report=False, quiet=True,
                        unsafe=True, parser=_parser)
    return parser


def _set_help_updates_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for service update check subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("help-updates", help="check for service updates",
                             description="request AUR for current version and compare with current service version",
                             formatter_class=_formatter)
    parser.add_argument("-e", "--exit-code", help="return non-zero exit code if updates available", action="store_true")
    parser.set_defaults(handler=handlers.ServiceUpdates, architecture=[""], lock=None, report=False, quiet=True,
                        unsafe=True)
    return parser


def _set_help_version_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for version subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("help-version", aliases=["version"], help="application version",
                             description="print application and its dependencies versions", formatter_class=_formatter)
    parser.set_defaults(handler=handlers.Versions, architecture=[""], lock=None, report=False, quiet=True, unsafe=True)
    return parser


def _set_package_add_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for package addition subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
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
    parser.add_argument("--dependencies", help="process missing package dependencies",
                        action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("-e", "--exit-code", help="return non-zero exit status if result is empty", action="store_true")
    parser.add_argument("-n", "--now", help="run update function after", action="store_true")
    parser.add_argument("-y", "--refresh", help="download fresh package databases from the mirror before actions, "
                                                "-yy to force refresh even if up to date",
                        action="count", default=False)
    parser.add_argument("-s", "--source", help="explicitly specify the package source for this command",
                        type=PackageSource, choices=enum_values(PackageSource), default=PackageSource.Auto)
    parser.set_defaults(handler=handlers.Add)
    return parser


def _set_package_remove_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for package removal subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("package-remove", aliases=["remove"], help="remove package",
                             description="remove package from the repository", formatter_class=_formatter)
    parser.add_argument("package", help="package name or base", nargs="+")
    parser.set_defaults(handler=handlers.Remove)
    return parser


def _set_package_status_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for package status subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("package-status", aliases=["status"], help="get package status",
                             description="request status of the package",
                             epilog="This feature requests package status from the web interface if it is available.",
                             formatter_class=_formatter)
    parser.add_argument("package", help="filter status by package base", nargs="*")
    parser.add_argument("--ahriman", help="get service status itself", action="store_true")
    parser.add_argument("-e", "--exit-code", help="return non-zero exit status if result is empty", action="store_true")
    parser.add_argument("--info", help="show additional package information",
                        action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("-s", "--status", help="filter packages by status",
                        type=BuildStatusEnum, choices=enum_values(BuildStatusEnum))
    parser.set_defaults(handler=handlers.Status, lock=None, report=False, quiet=True, unsafe=True)
    return parser


def _set_package_status_remove_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for package status remove subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("package-status-remove", help="remove package status",
                             description="remove the package from the status page",
                             epilog="Please note that this subcommand does not remove the package itself, it just "
                                    "clears the status page.",
                             formatter_class=_formatter)
    parser.add_argument("package", help="remove specified packages from status page", nargs="+")
    parser.set_defaults(handler=handlers.StatusUpdate, action=Action.Remove, lock=None, report=False, quiet=True,
                        unsafe=True)
    return parser


def _set_package_status_update_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for package status update subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("package-status-update", aliases=["status-update"], help="update package status",
                             description="update package status on the status page", formatter_class=_formatter)
    parser.add_argument("package", help="set status for specified packages. "
                                        "If no packages supplied, service status will be updated",
                        nargs="*")
    parser.add_argument("-s", "--status", help="new package build status",
                        type=BuildStatusEnum, choices=enum_values(BuildStatusEnum), default=BuildStatusEnum.Success)
    parser.set_defaults(handler=handlers.StatusUpdate, action=Action.Update, lock=None, report=False, quiet=True,
                        unsafe=True)
    return parser


def _set_patch_add_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for new single-function patch subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("patch-add", help="add patch for PKGBUILD function",
                             description="create or update patched PKGBUILD function or variable",
                             epilog="Unlike ``patch-set-add``, this function allows to patch only one PKGBUILD "
                                    "function, e.g. typing ``ahriman patch-add ahriman pkgver`` it will change the "
                                    "``pkgver`` inside PKGBUILD, typing ``ahriman patch-add ahriman build()`` "
                                    "it will change ``build()`` function inside PKGBUILD",
                             formatter_class=_formatter)
    parser.add_argument("package", help="package base")
    parser.add_argument("variable", help="PKGBUILD variable or function name. If variable is a function, "
                                         "it must end with ()")
    parser.add_argument("patch", help="path to file which contains function or variable value. If not set, "
                                      "the value will be read from stdin", type=Path, nargs="?")
    parser.set_defaults(handler=handlers.Patch, action=Action.Update, architecture=[""], lock=None, report=False)
    return parser


def _set_patch_list_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for list patches subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("patch-list", help="list patch sets",
                             description="list available patches for the package", formatter_class=_formatter)
    parser.add_argument("package", help="package base", nargs="?")
    parser.add_argument("-e", "--exit-code", help="return non-zero exit status if result is empty", action="store_true")
    parser.add_argument("-v", "--variable", help="if set, show only patches for specified PKGBUILD variables",
                        action="append")
    parser.set_defaults(handler=handlers.Patch, action=Action.List, architecture=[""], lock=None, report=False,
                        unsafe=True)
    return parser


def _set_patch_remove_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for remove patches subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("patch-remove", help="remove patch set", description="remove patches for the package",
                             formatter_class=_formatter)
    parser.add_argument("package", help="package base")
    parser.add_argument("-v", "--variable", help="should be used for single-function patches in case if you wold like "
                                                 "to remove only specified PKGBUILD variables. In case if not set, "
                                                 "it will remove all patches related to the package",
                        action="append")
    parser.set_defaults(handler=handlers.Patch, action=Action.Remove, architecture=[""], lock=None, report=False)
    return parser


def _set_patch_set_add_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for new full-diff patch subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("patch-set-add", help="add patch set", description="create or update source patches",
                             epilog="In order to add a patch set for the package you will need to clone "
                                    "the AUR package manually, add required changes (e.g. external patches, "
                                    "edit PKGBUILD) and run command, e.g. ``ahriman patch-set-add path/to/directory``. "
                                    "By default it tracks *.patch and *.diff files, but this behavior can be changed "
                                    "by using --track option",
                             formatter_class=_formatter)
    parser.add_argument("package", help="path to directory with changed files for patch addition/update", type=Path)
    parser.add_argument("-t", "--track", help="files which has to be tracked", action="append",
                        default=["*.diff", "*.patch"])
    parser.set_defaults(handler=handlers.Patch, action=Action.Update, architecture=[""], lock=None, report=False,
                        variable=None)
    return parser


def _set_repo_backup_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for repository backup subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("repo-backup", help="backup repository data",
                             description="backup repository settings and database", formatter_class=_formatter)
    parser.add_argument("path", help="path of the output archive", type=Path)
    parser.set_defaults(handler=handlers.Backup, architecture=[""], lock=None, report=False, unsafe=True)
    return parser


def _set_repo_check_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for repository check subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("repo-check", aliases=["check"], help="check for updates",
                             description="check for packages updates. Same as repo-update --dry-run --no-manual",
                             formatter_class=_formatter)
    parser.add_argument("package", help="filter check by package base", nargs="*")
    parser.add_argument("-e", "--exit-code", help="return non-zero exit status if result is empty", action="store_true")
    parser.add_argument("--vcs", help="fetch actual version of VCS packages",
                        action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("-y", "--refresh", help="download fresh package databases from the mirror before actions, "
                                                "-yy to force refresh even if up to date",
                        action="count", default=False)
    parser.set_defaults(handler=handlers.Update, dependencies=False, dry_run=True, aur=True, local=True, manual=False)
    return parser


def _set_repo_daemon_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for daemon subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("repo-daemon", aliases=["daemon"], help="run application as daemon",
                             description="start process which periodically will run update process",
                             formatter_class=_formatter)
    parser.add_argument("-i", "--interval", help="interval between runs in seconds", type=int, default=60 * 60 * 12)
    parser.add_argument("--aur", help="enable or disable checking for AUR updates",
                        action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--dependencies", help="process missing package dependencies",
                        action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--local", help="enable or disable checking of local packages for updates",
                        action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--manual", help="include or exclude manual updates",
                        action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--vcs", help="fetch actual version of VCS packages",
                        action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("-y", "--refresh", help="download fresh package databases from the mirror before actions, "
                                                "-yy to force refresh even if up to date",
                        action="count", default=False)
    parser.set_defaults(handler=handlers.Daemon, dry_run=False, exit_code=False, package=[])
    return parser


def _set_repo_rebuild_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for repository rebuild subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("repo-rebuild", aliases=["rebuild"], help="rebuild repository",
                             description="force rebuild whole repository", formatter_class=_formatter)
    parser.add_argument("--depends-on", help="only rebuild packages that depend on specified packages", action="append")
    parser.add_argument("--dry-run", help="just perform check for packages without rebuild process itself",
                        action="store_true")
    parser.add_argument("--from-database",
                        help="read packages from database instead of filesystem. This feature in particular is "
                             "required in case if you would like to restore repository from another repository "
                             "instance. Note, however, that in order to restore packages you need to have original "
                             "ahriman instance run with web service and have run repo-update at least once.",
                        action="store_true")
    parser.add_argument("-e", "--exit-code", help="return non-zero exit status if result is empty", action="store_true")
    parser.set_defaults(handler=handlers.Rebuild)
    return parser


def _set_repo_remove_unknown_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for remove unknown packages subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("repo-remove-unknown", aliases=["remove-unknown"], help="remove unknown packages",
                             description="remove packages which are missing in AUR and do not have local PKGBUILDs",
                             formatter_class=_formatter)
    parser.add_argument("--dry-run", help="just perform check for packages without removal", action="store_true")
    parser.set_defaults(handler=handlers.RemoveUnknown)
    return parser


def _set_repo_report_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for report subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("repo-report", aliases=["report"], help="generate report",
                             description="generate repository report according to current settings",
                             epilog="Create and/or update repository report as configured.",
                             formatter_class=_formatter)
    parser.set_defaults(handler=handlers.Triggers, trigger=["ahriman.core.report.ReportTrigger"])
    return parser


def _set_repo_restore_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for repository restore subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("repo-restore", help="restore repository data",
                             description="restore settings and database", formatter_class=_formatter)
    parser.add_argument("path", help="path of the input archive", type=Path)
    parser.add_argument("-o", "--output", help="root path of the extracted files", type=Path, default=Path("/"))
    parser.set_defaults(handler=handlers.Restore, architecture=[""], lock=None, report=False, unsafe=True)
    return parser


def _set_repo_sign_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for sign subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
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

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("repo-status-update", help="update repository status",
                             description="update repository status on the status page", formatter_class=_formatter)
    parser.add_argument("-s", "--status", help="new status",
                        type=BuildStatusEnum, choices=enum_values(BuildStatusEnum), default=BuildStatusEnum.Success)
    parser.set_defaults(handler=handlers.StatusUpdate, action=Action.Update, lock=None, report=False, package=[],
                        quiet=True, unsafe=True)
    return parser


def _set_repo_sync_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for repository sync subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("repo-sync", aliases=["sync"], help="sync repository",
                             description="sync repository files to remote server according to current settings",
                             epilog="Synchronize the repository to remote services as configured.",
                             formatter_class=_formatter)
    parser.set_defaults(handler=handlers.Triggers, trigger=["ahriman.core.upload.UploadTrigger"])
    return parser


def _set_repo_tree_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for repository tree subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("repo-tree", help="dump repository tree",
                             description="dump repository tree based on packages dependencies",
                             formatter_class=_formatter)
    parser.set_defaults(handler=handlers.Structure, lock=None, report=False, quiet=True, unsafe=True)
    return parser


def _set_repo_triggers_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for repository triggers subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("repo-triggers", help="run triggers",
                             description="run triggers on empty build result as configured by settings",
                             formatter_class=_formatter)
    parser.add_argument("trigger", help="instead of running all triggers as set by configuration, just process "
                                        "specified ones in order of mention", nargs="*")
    parser.set_defaults(handler=handlers.Triggers)
    return parser


def _set_repo_update_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for repository update subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("repo-update", aliases=["update"], help="update packages",
                             description="check for packages updates and run build process if requested",
                             formatter_class=_formatter)
    parser.add_argument("package", help="filter check by package base", nargs="*")
    parser.add_argument("--aur", help="enable or disable checking for AUR updates",
                        action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--dependencies", help="process missing package dependencies",
                        action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--dry-run", help="just perform check for updates, same as check command", action="store_true")
    parser.add_argument("-e", "--exit-code", help="return non-zero exit status if result is empty", action="store_true")
    parser.add_argument("--local", help="enable or disable checking of local packages for updates",
                        action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--manual", help="include or exclude manual updates",
                        action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--vcs", help="fetch actual version of VCS packages",
                        action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("-y", "--refresh", help="download fresh package databases from the mirror before actions, "
                                                "-yy to force refresh even if up to date",
                        action="count", default=False)
    parser.set_defaults(handler=handlers.Update)
    return parser


def _set_service_clean_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for repository clean subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("service-clean", aliases=["clean", "repo-clean"], help="clean local caches",
                             description="remove local caches",
                             epilog="The subcommand clears every temporary directories (builds, caches etc). Normally "
                                    "you should not run this command manually. Also in case if you are going to clear "
                                    "the chroot directories you will need root privileges.",
                             formatter_class=_formatter)
    parser.add_argument("--cache", help="clear directory with package caches",
                        action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--chroot", help="clear build chroot", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--manual", help="clear manually added packages queue",
                        action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--packages", help="clear directory with built packages",
                        action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--pacman", help="clear directory with pacman local database cache",
                        action=argparse.BooleanOptionalAction, default=False)
    parser.set_defaults(handler=handlers.Clean, quiet=True, unsafe=True)
    return parser


def _set_service_config_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for config subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("service-config", aliases=["config", "repo-config"], help="dump configuration",
                             description="dump configuration for the specified architecture",
                             formatter_class=_formatter)
    parser.add_argument("--secure", help="hide passwords and secrets from output",
                        action=argparse.BooleanOptionalAction, default=True)
    parser.set_defaults(handler=handlers.Dump, lock=None, report=False, quiet=True, unsafe=True)
    return parser


def _set_service_config_validate_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for config validation subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("service-config-validate", aliases=["config-validate", "repo-config-validate"],
                             help="validate system configuration",
                             description="validate configuration and print found errors",
                             formatter_class=_formatter)
    parser.add_argument("-e", "--exit-code", help="return non-zero exit status if configuration is invalid",
                        action="store_true")
    parser.set_defaults(handler=handlers.Validate, lock=None, report=False, quiet=True, unsafe=True)
    return parser


def _set_service_key_import_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for key import subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("service-key-import", aliases=["key-import"], help="import PGP key",
                             description="import PGP key from public sources to the repository user",
                             epilog="By default ahriman runs build process with package sources validation "
                                    "(in case if signature and keys are available in PKGBUILD). This process will "
                                    "fail in case if key is not known for build user. This subcommand can be used "
                                    "in order to import the PGP key to user keychain.",
                             formatter_class=_formatter)
    parser.add_argument("--key-server", help="key server for key import", default="keyserver.ubuntu.com")
    parser.add_argument("key", help="PGP key to import from public server")
    parser.set_defaults(handler=handlers.KeyImport, architecture=[""], lock=None, report=False)
    return parser


def _set_service_setup_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for setup subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("service-setup", aliases=["init", "repo-init", "repo-setup", "setup"],
                             help="initial service configuration",
                             description="create initial service configuration, requires root",
                             epilog="Create _minimal_ configuration for the service according to provided options.",
                             formatter_class=_formatter)
    parser.add_argument("--build-command", help="path to build command", default=Path("/usr") / "bin" / "pkgctl")
    parser.add_argument("--from-configuration", help="path to default devtools pacman configuration", type=Path,
                        default=Path("/usr") / "local" / "share" / "devtools-git-poc" / "pacman.conf.d" / "extra.conf")
    parser.add_argument("--makeflags-jobs", help="append MAKEFLAGS variable with parallelism set to number of cores",
                        action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--mirror", help="use the specified explicitly mirror instead of including mirrorlist")
    parser.add_argument("--multilib", help="add or do not multilib repository",
                        action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--packager", help="packager name and email", required=True)
    parser.add_argument("--repository", help="repository name", required=True)
    parser.add_argument("--sign-key", help="sign key id")
    parser.add_argument("--sign-target", help="sign options", action="append",
                        type=SignSettings.from_option, choices=enum_values(SignSettings))
    parser.add_argument("--web-port", help="port of the web service", type=int)
    parser.add_argument("--web-unix-socket", help="path to unix socket used for interprocess communications", type=Path)
    parser.set_defaults(handler=handlers.Setup, lock=None, report=False, quiet=True, unsafe=True)
    return parser


def _set_service_shell_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for shell subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("service-shell", aliases=["shell"], help="invoke python shell",
                             description="drop into python shell while having created application",
                             formatter_class=_formatter)
    parser.add_argument("code", help="instead of dropping into shell, just execute the specified code", nargs="?")
    parser.add_argument("-v", "--verbose", help=argparse.SUPPRESS, action="store_true")
    parser.set_defaults(handler=handlers.Shell, lock=None, report=False)
    return parser


def _set_user_add_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for create user subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("user-add", help="create or update user",
                             description="update user for web services with the given password and role. "
                                         "In case if password was not entered it will be asked interactively",
                             epilog="In case of first run (i.e. if password salt is not set yet) this action requires "
                                    "root privileges because it performs write to filesystem configuration.",
                             formatter_class=_formatter)
    parser.add_argument("username", help="username for web service")
    parser.add_argument("-p", "--password", help="user password. Blank password will be treated as empty password, "
                                                 "which is in particular must be used for OAuth2 authorization type.")
    parser.add_argument("-r", "--role", help="user access level",
                        type=UserAccess, choices=enum_values(UserAccess), default=UserAccess.Read)
    parser.add_argument("-s", "--secure", help="set file permissions to user-only", action="store_true")
    parser.set_defaults(handler=handlers.Users, action=Action.Update, architecture=[""], lock=None, report=False,
                        quiet=True)
    return parser


def _set_user_list_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for user list subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("user-list", help="user known users and their access",
                             description="list users from the user mapping and their roles",
                             formatter_class=_formatter)
    parser.add_argument("username", help="filter users by username", nargs="?")
    parser.add_argument("-e", "--exit-code", help="return non-zero exit status if result is empty", action="store_true")
    parser.add_argument("-r", "--role", help="filter users by role", type=UserAccess, choices=enum_values(UserAccess))
    parser.set_defaults(handler=handlers.Users, action=Action.List, architecture=[""], lock=None, report=False,  # nosec
                        password="", quiet=True, unsafe=True)
    return parser


def _set_user_remove_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for user removal subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("user-remove", help="remove user",
                             description="remove user from the user mapping and update the configuration",
                             formatter_class=_formatter)
    parser.add_argument("username", help="username for web service")
    parser.set_defaults(handler=handlers.Users, action=Action.Remove, architecture=[""], lock=None, report=False,  # nosec
                        password="", quiet=True)
    return parser


def _set_web_parser(root: SubParserAction) -> argparse.ArgumentParser:
    """
    add parser for web subcommand

    Args:
        root(SubParserAction): subparsers for the commands

    Returns:
        argparse.ArgumentParser: created argument parser
    """
    parser = root.add_parser("web", help="web server", description="start web server", formatter_class=_formatter)
    parser.set_defaults(handler=handlers.Web, lock=Path(tempfile.gettempdir()) / "ahriman-web.lock", report=False,
                        parser=_parser)
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
