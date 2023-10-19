import argparse
import pytest

from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.application import ahriman
from ahriman.application.handlers import Handler
from ahriman.core.configuration import Configuration
from ahriman.models.action import Action
from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.log_handler import LogHandler
from ahriman.models.sign_settings import SignSettings
from ahriman.models.user_access import UserAccess


def test_parser(parser: argparse.ArgumentParser) -> None:
    """
    must parse valid command line
    """
    parser.parse_args(["-a", "x86_64", "-r", "repo", "service-config"])


def test_parser_option_configuration(parser: argparse.ArgumentParser) -> None:
    """
    must convert configuration option to Path instance
    """
    args = parser.parse_args(["-a", "x86_64", "-r", "repo", "service-config"])
    assert isinstance(args.configuration, Path)
    args = parser.parse_args(["-a", "x86_64", "-c", "ahriman.ini", "-r", "repo", "service-config"])
    assert isinstance(args.configuration, Path)


def test_parser_option_lock(parser: argparse.ArgumentParser) -> None:
    """
    must convert lock option to Path instance
    """
    args = parser.parse_args(["repo-update"])
    assert isinstance(args.lock, Path)
    args = parser.parse_args(["-l", "ahriman.lock", "repo-update"])
    assert isinstance(args.lock, Path)


def test_parser_option_log_handler(parser: argparse.ArgumentParser) -> None:
    """
    must convert log-handler option to LogHandler instance
    """
    args = parser.parse_args(["--log-handler", "console", "service-config"])
    assert isinstance(args.log_handler, LogHandler)


def test_parser_option_wait_timeout(parser: argparse.ArgumentParser) -> None:
    """
    must convert wait-timeout option to int instance
    """
    args = parser.parse_args(["service-config"])
    assert isinstance(args.wait_timeout, int)
    args = parser.parse_args(["--wait-timeout", "60", "service-config"])
    assert isinstance(args.wait_timeout, int)


def test_parser_option_architecture_empty(parser: argparse.ArgumentParser) -> None:
    """
    must parse empty architecture list as None
    """
    args = parser.parse_args(["service-config"])
    assert args.architecture is None


def test_parser_option_repository_empty(parser: argparse.ArgumentParser) -> None:
    """
    must parse empty repository list as None
    """
    args = parser.parse_args(["service-config"])
    assert args.repository is None


def test_subparsers_aur_search(parser: argparse.ArgumentParser) -> None:
    """
    aur-search command must imply architecture list, lock, quiet, report, repository and unsafe
    """
    args = parser.parse_args(["aur-search", "ahriman"])
    assert args.architecture == ""
    assert args.lock is None
    assert args.quiet
    assert not args.report
    assert args.repository == ""
    assert args.unsafe


def test_subparsers_aur_search_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    aur-search command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "aur-search", "ahriman"])
    assert args.architecture == ""


def test_subparsers_aur_search_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    aur-search command must correctly parse repository list
    """
    args = parser.parse_args(["-r", "repo", "aur-search", "ahriman"])
    assert args.repository == ""


def test_subparsers_help(parser: argparse.ArgumentParser) -> None:
    """
    help command must imply architecture list, lock, quiet, report, repository, unsafe and parser
    """
    args = parser.parse_args(["help"])
    assert args.architecture == ""
    assert args.lock is None
    assert args.quiet
    assert not args.report
    assert args.repository == ""
    assert args.unsafe
    assert args.parser is not None and args.parser()


def test_subparsers_help_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    help command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "help"])
    assert args.architecture == ""


def test_subparsers_help_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    help command must correctly parse repository list
    """
    args = parser.parse_args(["-r", "repo", "help"])
    assert args.repository == ""


def test_subparsers_help_commands_unsafe(parser: argparse.ArgumentParser) -> None:
    """
    help-commands-unsafe command must imply architecture list, lock, quiet, report, repository, unsafe and parser
    """
    args = parser.parse_args(["help-commands-unsafe"])
    assert args.architecture == ""
    assert args.lock is None
    assert args.quiet
    assert not args.report
    assert args.repository == ""
    assert args.unsafe
    assert args.parser is not None and args.parser()


def test_subparsers_help_commands_unsafe_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    help-commands-unsafe command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "help-commands-unsafe"])
    assert args.architecture == ""


def test_subparsers_help_commands_unsafe_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    help-commands-unsafe command must correctly parse repository list
    """
    args = parser.parse_args(["-r", "repo", "help-commands-unsafe"])
    assert args.repository == ""


def test_subparsers_help_updates(parser: argparse.ArgumentParser) -> None:
    """
    help-updates command must imply architecture list, lock, quiet, report, repository, and unsafe
    """
    args = parser.parse_args(["help-updates"])
    assert args.architecture == ""
    assert args.lock is None
    assert args.quiet
    assert not args.report
    assert args.repository == ""
    assert args.unsafe


def test_subparsers_help_updates_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    help-updates command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "help-updates"])
    assert args.architecture == ""


def test_subparsers_help_updates_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    help-updates command must correctly parse repository list
    """
    args = parser.parse_args(["-r", "repo", "help-updates"])
    assert args.repository == ""


def test_subparsers_help_version(parser: argparse.ArgumentParser) -> None:
    """
    help-version command must imply architecture, lock, quiet, report, repository and unsafe
    """
    args = parser.parse_args(["help-version"])
    assert args.architecture == ""
    assert args.lock is None
    assert args.quiet
    assert not args.report
    assert args.repository == ""
    assert args.unsafe


def test_subparsers_help_version_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    help-version command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "help-version"])
    assert args.architecture == ""


def test_subparsers_help_version_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    help-version command must correctly parse repository list
    """
    args = parser.parse_args(["-r", "repo", "help-version"])
    assert args.repository == ""


def test_subparsers_package_add_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    package-add command must correctly parse architecture list
    """
    args = parser.parse_args(["package-add", "ahriman"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "package-add", "ahriman"])
    assert args.architecture == "x86_64"


def test_subparsers_package_add_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    package-add command must correctly parse repository list
    """
    args = parser.parse_args(["package-add", "ahriman"])
    assert args.repository is None
    args = parser.parse_args(["-r", "repo", "package-add", "ahriman"])
    assert args.repository == "repo"


def test_subparsers_package_add_option_refresh(parser: argparse.ArgumentParser) -> None:
    """
    package-add command must count refresh options
    """
    args = parser.parse_args(["package-add", "ahriman"])
    assert args.refresh == 0
    args = parser.parse_args(["package-add", "ahriman", "-y"])
    assert args.refresh == 1
    args = parser.parse_args(["package-add", "ahriman", "-yy"])
    assert args.refresh == 2


def test_subparsers_package_remove_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    package-remove command must correctly parse architecture list
    """
    args = parser.parse_args(["package-remove", "ahriman"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "package-remove", "ahriman"])
    assert args.architecture == "x86_64"


def test_subparsers_package_remove_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    package-remove command must correctly parse repository list
    """
    args = parser.parse_args(["package-remove", "ahriman"])
    assert args.repository is None
    args = parser.parse_args(["-r", "repo", "package-remove", "ahriman"])
    assert args.repository == "repo"


def test_subparsers_package_status(parser: argparse.ArgumentParser) -> None:
    """
    package-status command must imply lock, quiet, report and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "-r", "repo", "package-status"])
    assert args.architecture == "x86_64"
    assert args.lock is None
    assert args.quiet
    assert not args.report
    assert args.repository == "repo"
    assert args.unsafe


def test_subparsers_package_status_remove(parser: argparse.ArgumentParser) -> None:
    """
    package-status-remove command must imply action, lock, quiet, report and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "-r", "repo", "package-status-remove", "ahriman"])
    assert args.architecture == "x86_64"
    assert args.action == Action.Remove
    assert args.lock is None
    assert args.quiet
    assert not args.report
    assert args.repository == "repo"
    assert args.unsafe


def test_subparsers_package_status_update(parser: argparse.ArgumentParser) -> None:
    """
    package-status-update command must imply action, lock, quiet, report and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "-r", "repo", "package-status-update"])
    assert args.architecture == "x86_64"
    assert args.action == Action.Update
    assert args.lock is None
    assert args.quiet
    assert not args.report
    assert args.repository == "repo"
    assert args.unsafe


def test_subparsers_package_status_update_option_status(parser: argparse.ArgumentParser) -> None:
    """
    package-status-update command must convert status option to buildstatusenum instance
    """
    args = parser.parse_args(["-a", "x86_64", "-r", "repo", "package-status-update"])
    assert isinstance(args.status, BuildStatusEnum)
    args = parser.parse_args(["-a", "x86_64", "-r", "repo", "package-status-update", "--status", "failed"])
    assert isinstance(args.status, BuildStatusEnum)


def test_subparsers_patch_add(parser: argparse.ArgumentParser) -> None:
    """
    patch-add command must imply action, architecture list, lock, report and repository
    """
    args = parser.parse_args(["patch-add", "ahriman", "version"])
    assert args.action == Action.Update
    assert args.architecture == ""
    assert args.lock is None
    assert not args.report
    assert args.repository == ""


def test_subparsers_patch_add_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    patch-add command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "patch-add", "ahriman", "version"])
    assert args.architecture == ""


def test_subparsers_patch_add_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    patch-add command must correctly parse repository list
    """
    args = parser.parse_args(["-r", "repo", "patch-add", "ahriman", "version"])
    assert args.repository == ""


def test_subparsers_patch_list(parser: argparse.ArgumentParser) -> None:
    """
    patch-list command must imply action, architecture list, lock, report, repository and unsafe
    """
    args = parser.parse_args(["patch-list", "ahriman"])
    assert args.action == Action.List
    assert args.architecture == ""
    assert args.lock is None
    assert not args.report
    assert args.repository == ""
    assert args.unsafe


def test_subparsers_patch_list_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    patch-list command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "patch-list", "ahriman"])
    assert args.architecture == ""


def test_subparsers_patch_list_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    patch-list command must correctly parse repository list
    """
    args = parser.parse_args(["-r", "repo", "patch-list", "ahriman"])
    assert args.repository == ""


def test_subparsers_patch_list_option_variable_empty(parser: argparse.ArgumentParser) -> None:
    """
    patch-list command must accept empty variable list as None
    """
    args = parser.parse_args(["patch-list", "ahriman"])
    assert args.variable is None


def test_subparsers_patch_list_option_variable_multiple(parser: argparse.ArgumentParser) -> None:
    """
    patch-list command must accept multiple variables
    """
    args = parser.parse_args(["patch-list", "-v", "var1", "-v", "var2", "ahriman"])
    assert args.variable == ["var1", "var2"]


def test_subparsers_patch_remove(parser: argparse.ArgumentParser) -> None:
    """
    patch-remove command must imply action, architecture list, lock, report and repository
    """
    args = parser.parse_args(["patch-remove", "ahriman"])
    assert args.action == Action.Remove
    assert args.architecture == ""
    assert args.lock is None
    assert not args.report
    assert args.repository == ""


def test_subparsers_patch_remove_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    patch-remove command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "patch-remove", "ahriman"])
    assert args.architecture == ""


def test_subparsers_patch_remove_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    patch-remove command must correctly parse repository list
    """
    args = parser.parse_args(["-r", "repo", "patch-remove", "ahriman"])
    assert args.repository == ""


def test_subparsers_patch_remove_option_variable_empty(parser: argparse.ArgumentParser) -> None:
    """
    patch-remove command must accept empty variable list as None
    """
    args = parser.parse_args(["patch-remove", "ahriman"])
    assert args.variable is None


def test_subparsers_patch_remove_option_variable_multiple(parser: argparse.ArgumentParser) -> None:
    """
    patch-remove command must accept multiple variables
    """
    args = parser.parse_args(["patch-remove", "-v", "var1", "-v", "var2", "ahriman"])
    assert args.variable == ["var1", "var2"]


def test_subparsers_patch_set_add(parser: argparse.ArgumentParser) -> None:
    """
    patch-set-add command must imply action, architecture list, lock, report, repository and variable
    """
    args = parser.parse_args(["patch-set-add", "ahriman"])
    assert args.action == Action.Update
    assert args.architecture == ""
    assert args.lock is None
    assert not args.report
    assert args.repository == ""
    assert args.variable is None


def test_subparsers_patch_set_add_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    patch-set-add command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "patch-set-add", "ahriman"])
    assert args.architecture == ""


def test_subparsers_patch_set_add_option_package(parser: argparse.ArgumentParser) -> None:
    """
    patch-set-add command must convert package option to path instance
    """
    args = parser.parse_args(["patch-set-add", "ahriman"])
    assert isinstance(args.package, Path)


def test_subparsers_patch_set_add_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    patch-set-add command must correctly parse repository list
    """
    args = parser.parse_args(["-r", "repo", "patch-set-add", "ahriman"])
    assert args.repository == ""


def test_subparsers_patch_set_add_option_track(parser: argparse.ArgumentParser) -> None:
    """
    patch-set-add command must correctly parse track files patterns
    """
    args = parser.parse_args(["patch-set-add", "-t", "*.py", "ahriman"])
    assert args.track == ["*.diff", "*.patch", "*.py"]


def test_subparsers_repo_backup(parser: argparse.ArgumentParser) -> None:
    """
    repo-backup command must imply architecture list, lock, report, repository and unsafe
    """
    args = parser.parse_args(["repo-backup", "output.zip"])
    assert args.architecture == ""
    assert args.lock is None
    assert not args.report
    assert args.repository == ""
    assert args.unsafe


def test_subparsers_repo_backup_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-backup command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "repo-backup", "output.zip"])
    assert args.architecture == ""


def test_subparsers_repo_backup_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    repo-backup command must correctly parse repository list
    """
    args = parser.parse_args(["-r", "repo", "repo-backup", "output.zip"])
    assert args.repository == ""


def test_subparsers_repo_check(parser: argparse.ArgumentParser) -> None:
    """
    repo-check command must imply dependencies, dry-run, aur, manual and username
    """
    args = parser.parse_args(["repo-check"])
    assert not args.dependencies
    assert args.dry_run
    assert args.aur
    assert not args.manual
    assert args.username is None


def test_subparsers_repo_check_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-check command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-check"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "repo-check"])
    assert args.architecture == "x86_64"


def test_subparsers_repo_check_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    repo-check command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-check"])
    assert args.repository is None
    args = parser.parse_args(["-r", "repo", "repo-check"])
    assert args.repository == "repo"


def test_subparsers_repo_check_option_refresh(parser: argparse.ArgumentParser) -> None:
    """
    repo-check command must count refresh options
    """
    args = parser.parse_args(["repo-check"])
    assert args.refresh == 0
    args = parser.parse_args(["repo-check", "-y"])
    assert args.refresh == 1
    args = parser.parse_args(["repo-check", "-yy"])
    assert args.refresh == 2


def test_subparsers_repo_create_keyring(parser: argparse.ArgumentParser) -> None:
    """
    repo-create-keyring command must imply trigger
    """
    args = parser.parse_args(["repo-create-keyring"])
    assert args.trigger == ["ahriman.core.support.KeyringTrigger"]


def test_subparsers_repo_create_keyring_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-create-keyring command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-create-keyring"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "repo-create-keyring"])
    assert args.architecture == "x86_64"


def test_subparsers_repo_create_keyring_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    repo-create-keyring command must correctly parse repository list
    """
    args = parser.parse_args(["repo-create-keyring"])
    assert args.repository is None
    args = parser.parse_args(["-r", "repo", "repo-create-keyring"])
    assert args.repository == "repo"


def test_subparsers_repo_create_mirrorlist(parser: argparse.ArgumentParser) -> None:
    """
    repo-create-mirrorlist command must imply trigger
    """
    args = parser.parse_args(["repo-create-mirrorlist"])
    assert args.trigger == ["ahriman.core.support.MirrorlistTrigger"]


def test_subparsers_repo_create_mirrorlist_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-create-mirrorlist command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-create-mirrorlist"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "repo-create-mirrorlist"])
    assert args.architecture == "x86_64"


def test_subparsers_repo_create_mirrorlist_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    repo-create-mirrorlist command must correctly parse repository list
    """
    args = parser.parse_args(["repo-create-mirrorlist"])
    assert args.repository is None
    args = parser.parse_args(["-r", "repo", "repo-create-mirrorlist"])
    assert args.repository == "repo"


def test_subparsers_repo_daemon(parser: argparse.ArgumentParser) -> None:
    """
    repo-daemon command must imply dry run, exit code and package
    """
    args = parser.parse_args(["repo-daemon"])
    assert not args.dry_run
    assert not args.exit_code
    assert args.package == []


def test_subparsers_repo_daemon_option_refresh(parser: argparse.ArgumentParser) -> None:
    """
    repo-daemon command must count refresh options
    """
    args = parser.parse_args(["repo-daemon"])
    assert args.refresh == 0
    args = parser.parse_args(["repo-daemon", "-y"])
    assert args.refresh == 1
    args = parser.parse_args(["repo-daemon", "-yy"])
    assert args.refresh == 2


def test_subparsers_repo_daemon_option_interval(parser: argparse.ArgumentParser) -> None:
    """
    repo-daemon command must convert interval option to int instance
    """
    args = parser.parse_args(["repo-daemon"])
    assert isinstance(args.interval, int)
    args = parser.parse_args(["repo-daemon", "--interval", "10"])
    assert isinstance(args.interval, int)


def test_subparsers_repo_rebuild_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-rebuild command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-rebuild"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "repo-rebuild"])
    assert args.architecture == "x86_64"


def test_subparsers_repo_rebuild_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    repo-rebuild command must correctly parse repository list
    """
    args = parser.parse_args(["repo-rebuild"])
    assert args.repository is None
    args = parser.parse_args(["-r", "repo", "repo-rebuild"])
    assert args.repository == "repo"


def test_subparsers_repo_rebuild_option_depends_on_empty(parser: argparse.ArgumentParser) -> None:
    """
    repo-rebuild command must accept empty depends-on list as None
    """
    args = parser.parse_args(["repo-rebuild"])
    assert args.depends_on is None


def test_subparsers_repo_rebuild_option_depends_on_multiple(parser: argparse.ArgumentParser) -> None:
    """
    repo-rebuild command must accept multiple depends-on
    """
    args = parser.parse_args(["repo-rebuild", "--depends-on", "package1", "--depends-on", "package2"])
    assert args.depends_on == ["package1", "package2"]


def test_subparsers_repo_rebuild_option_status(parser: argparse.ArgumentParser) -> None:
    """
    repo-rebuild command must convert status option to BuildStatusEnum instance
    """
    args = parser.parse_args(["-a", "x86_64", "-r", "repo", "repo-rebuild", "--status", "failed"])
    assert isinstance(args.status, BuildStatusEnum)


def test_subparsers_repo_remove_unknown_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-remove-unknown command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-remove-unknown"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "repo-remove-unknown"])
    assert args.architecture == "x86_64"


def test_subparsers_repo_remove_unknown_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    repo-remove-unknown command must correctly parse repository list
    """
    args = parser.parse_args(["repo-remove-unknown"])
    assert args.repository is None
    args = parser.parse_args(["-r", "repo", "repo-remove-unknown"])
    assert args.repository == "repo"


def test_subparsers_repo_report(parser: argparse.ArgumentParser) -> None:
    """
    repo-report command must imply trigger
    """
    args = parser.parse_args(["repo-report"])
    assert args.trigger == ["ahriman.core.report.ReportTrigger"]


def test_subparsers_repo_report_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-report command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-report"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "repo-report"])
    assert args.architecture == "x86_64"


def test_subparsers_repo_report_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    repo-report command must correctly parse repository list
    """
    args = parser.parse_args(["repo-report"])
    assert args.repository is None
    args = parser.parse_args(["-r", "repo", "repo-report"])
    assert args.repository == "repo"


def test_subparsers_repo_restore(parser: argparse.ArgumentParser) -> None:
    """
    repo-restore command must imply architecture list, lock, report, repository and unsafe
    """
    args = parser.parse_args(["repo-restore", "output.zip"])
    assert args.architecture == ""
    assert args.lock is None
    assert not args.report
    assert args.repository == ""
    assert args.unsafe


def test_subparsers_repo_restore_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-restore command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "repo-restore", "output.zip"])
    assert args.architecture == ""


def test_subparsers_repo_restore_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    repo-restore command must correctly parse repository list
    """
    args = parser.parse_args(["-r", "repo", "repo-restore", "output.zip"])
    assert args.repository == ""


def test_subparsers_repo_sign_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-sign command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-sign"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "repo-sign"])
    assert args.architecture == "x86_64"


def test_subparsers_repo_sign_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    repo-sign command must correctly parse repository list
    """
    args = parser.parse_args(["repo-sign"])
    assert args.repository is None
    args = parser.parse_args(["-r", "repo", "repo-sign"])
    assert args.repository == "repo"


def test_subparsers_repo_status_update(parser: argparse.ArgumentParser) -> None:
    """
    re[p-status-update command must imply action, lock, quiet, report, package and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "-r", "repo", "package-status-update"])
    assert args.architecture == "x86_64"
    assert args.action == Action.Update
    assert args.lock is None
    assert args.quiet
    assert not args.report
    assert args.repository == "repo"
    assert not args.package
    assert args.unsafe


def test_subparsers_repo_status_update_option_status(parser: argparse.ArgumentParser) -> None:
    """
    repo-status-update command must convert status option to BuildStatusEnum instance
    """
    args = parser.parse_args(["-a", "x86_64", "-r", "repo", "repo-status-update"])
    assert isinstance(args.status, BuildStatusEnum)
    args = parser.parse_args(["-a", "x86_64", "-r", "repo", "repo-status-update", "--status", "failed"])
    assert isinstance(args.status, BuildStatusEnum)


def test_subparsers_repo_sync(parser: argparse.ArgumentParser) -> None:
    """
    repo-sync command must imply trigger
    """
    args = parser.parse_args(["repo-sync"])
    assert args.trigger == ["ahriman.core.upload.UploadTrigger"]


def test_subparsers_repo_sync_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-sync command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-sync"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "repo-sync"])
    assert args.architecture == "x86_64"


def test_subparsers_repo_sync_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    repo-sync command must correctly parse repository list
    """
    args = parser.parse_args(["repo-sync"])
    assert args.repository is None
    args = parser.parse_args(["-r", "repo", "repo-sync"])
    assert args.repository == "repo"


def test_subparsers_repo_tree(parser: argparse.ArgumentParser) -> None:
    """
    repo-tree command must imply lock, quiet, report and unsafe
    """
    args = parser.parse_args(["repo-tree"])
    assert args.lock is None
    assert args.quiet
    assert not args.report
    assert args.unsafe


def test_subparsers_repo_tree_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-tree command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-tree"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "repo-tree"])
    assert args.architecture == "x86_64"


def test_subparsers_repo_tree_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    repo-tree command must correctly parse repository list
    """
    args = parser.parse_args(["repo-tree"])
    assert args.repository is None
    args = parser.parse_args(["-r", "repo", "repo-tree"])
    assert args.repository == "repo"


def test_subparsers_repo_tree_option_partitions(parser: argparse.ArgumentParser) -> None:
    """
    must convert partitions option to int instance
    """
    args = parser.parse_args(["repo-tree"])
    assert isinstance(args.partitions, int)
    args = parser.parse_args(["repo-tree", "--partitions", "42"])
    assert isinstance(args.partitions, int)


def test_subparsers_repo_triggers_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-triggers command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-triggers"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "repo-triggers"])
    assert args.architecture == "x86_64"


def test_subparsers_repo_triggers_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    repo-triggers command must correctly parse repository list
    """
    args = parser.parse_args(["repo-triggers"])
    assert args.repository is None
    args = parser.parse_args(["-r", "repo", "repo-triggers"])
    assert args.repository == "repo"


def test_subparsers_repo_update_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-update command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-update"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "repo-update"])
    assert args.architecture == "x86_64"


def test_subparsers_repo_update_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    repo-update command must correctly parse repository list
    """
    args = parser.parse_args(["repo-update"])
    assert args.repository is None
    args = parser.parse_args(["-r", "repo", "repo-update"])
    assert args.repository == "repo"


def test_subparsers_repo_update_option_refresh(parser: argparse.ArgumentParser) -> None:
    """
    repo-update command must count refresh options
    """
    args = parser.parse_args(["repo-update"])
    assert args.refresh == 0
    args = parser.parse_args(["repo-update", "-y"])
    assert args.refresh == 1
    args = parser.parse_args(["repo-update", "-yy"])
    assert args.refresh == 2


def test_subparsers_service_clean(parser: argparse.ArgumentParser) -> None:
    """
    service-clean command must imply quiet and unsafe
    """
    args = parser.parse_args(["service-clean"])
    assert args.quiet
    assert args.unsafe


def test_subparsers_service_clean_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    service-clean command must correctly parse architecture list
    """
    args = parser.parse_args(["service-clean"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "service-clean"])
    assert args.architecture == "x86_64"


def test_subparsers_service_clean_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    service-clean command must correctly parse repository list
    """
    args = parser.parse_args(["service-clean"])
    assert args.repository is None
    args = parser.parse_args(["-r", "repo", "service-clean"])
    assert args.repository == "repo"


def test_subparsers_service_config(parser: argparse.ArgumentParser) -> None:
    """
    service-config command must imply lock, quiet, report and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "-r", "repo", "service-config"])
    assert args.architecture == "x86_64"
    assert args.lock is None
    assert args.quiet
    assert not args.report
    assert args.repository == "repo"
    assert args.unsafe


def test_subparsers_service_config_option_section_key(parser: argparse.ArgumentParser) -> None:
    """
    service-config command must parse optional section and key arguments
    """
    args = parser.parse_args(["-a", "x86_64", "-r", "repo", "service-config"])
    assert args.section is None
    assert args.key is None

    args = parser.parse_args(["-a", "x86_64", "-r", "repo", "service-config", "section"])
    assert args.section == "section"
    assert args.key is None

    args = parser.parse_args(["-a", "x86_64", "-r", "repo", "service-config", "section", "key"])
    assert args.section == "section"
    assert args.key == "key"


def test_subparsers_service_config_validate(parser: argparse.ArgumentParser) -> None:
    """
    service-config-validate command must imply lock, quiet, report and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "-r", "repo", "service-config-validate"])
    assert args.architecture == "x86_64"
    assert args.lock is None
    assert args.quiet
    assert not args.report
    assert args.repository == "repo"
    assert args.unsafe


def test_subparsers_service_key_import(parser: argparse.ArgumentParser) -> None:
    """
    service-key-import command must imply architecture list, lock, report and repository
    """
    args = parser.parse_args(["service-key-import", "key"])
    assert args.architecture == ""
    assert args.lock is None
    assert not args.report
    assert args.repository == ""


def test_subparsers_service_key_import_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    service-key-import command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "service-key-import", "key"])
    assert args.architecture == ""


def test_subparsers_service_key_import_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    service-key-import command must correctly parse repository list
    """
    args = parser.parse_args(["-r", "repo", "service-key-import", "key"])
    assert args.repository == ""


def test_subparsers_service_repositories(parser: argparse.ArgumentParser) -> None:
    """
    service-repositories command must imply architecture, lock, report, repository and unsafe
    """
    args = parser.parse_args(["service-repositories"])
    assert args.architecture == ""
    assert args.lock is None
    assert not args.report
    assert args.repository == ""
    assert args.unsafe


def test_subparsers_service_repositories_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    service-repositories command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "service-repositories"])
    assert args.architecture == ""


def test_subparsers_service_repositories_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    service-repositories command must correctly parse repository list
    """
    args = parser.parse_args(["-r", "repo", "service-repositories"])
    assert args.repository == ""


def test_subparsers_service_run(parser: argparse.ArgumentParser) -> None:
    """
    service-run command must imply architecture, lock, report, repository and parser
    """
    args = parser.parse_args(["service-run", "help"])
    assert args.architecture == ""
    assert args.lock is None
    assert not args.report
    assert args.repository == ""
    assert args.parser is not None and args.parser()


def test_subparsers_service_run_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    service-run command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "service-run", "help"])
    assert args.architecture == ""


def test_subparsers_service_run_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    service-run command must correctly parse repository list
    """
    args = parser.parse_args(["-r", "repo", "service-run", "help"])
    assert args.repository == ""


def test_subparsers_service_setup(parser: argparse.ArgumentParser) -> None:
    """
    service-setup command must imply lock, quiet, report and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "-r", "repo", "service-setup", "--packager", "John Doe <john@doe.com>"])
    assert args.architecture == "x86_64"
    assert args.lock is None
    assert args.quiet
    assert not args.report
    assert args.repository == "repo"
    assert args.unsafe


def test_subparsers_service_setup_option_from_configuration(parser: argparse.ArgumentParser) -> None:
    """
    service-setup command must convert from-configuration option to path instance
    """
    args = parser.parse_args(["-a", "x86_64", "-r", "repo", "service-setup", "--packager", "John Doe <john@doe.com>"])
    assert isinstance(args.from_configuration, Path)
    args = parser.parse_args(["-a", "x86_64", "-r", "repo", "service-setup", "--packager", "John Doe <john@doe.com>",
                              "--from-configuration", "path"])
    assert isinstance(args.from_configuration, Path)


def test_subparsers_service_setup_option_sign_target(parser: argparse.ArgumentParser) -> None:
    """
    service-setup command must convert sign-target option to SignSettings instance
    """
    args = parser.parse_args(["-a", "x86_64", "-r", "repo", "service-setup", "--packager", "John Doe <john@doe.com>",
                              "--sign-target", "packages"])
    assert args.sign_target
    assert all(isinstance(target, SignSettings) for target in args.sign_target)


def test_subparsers_service_setup_option_sign_target_empty(parser: argparse.ArgumentParser) -> None:
    """
    service-setup command must accept empty sign-target list as None
    """
    args = parser.parse_args(["-a", "x86_64", "-r", "repo", "service-setup", "--packager", "John Doe <john@doe.com>"])
    assert args.sign_target is None


def test_subparsers_service_setup_option_sign_target_multiple(parser: argparse.ArgumentParser) -> None:
    """
    service-setup command must accept multiple sign-target
    """
    args = parser.parse_args(["-a", "x86_64", "-r", "repo", "service-setup", "--packager", "John Doe <john@doe.com>",
                              "--sign-target", "packages", "--sign-target", "repository"])
    assert args.sign_target == [SignSettings.Packages, SignSettings.Repository]


def test_subparsers_service_shell(parser: argparse.ArgumentParser) -> None:
    """
    service-shell command must imply lock and report
    """
    args = parser.parse_args(["service-shell"])
    assert args.lock is None
    assert not args.report


def test_subparsers_service_tree_migrate(parser: argparse.ArgumentParser) -> None:
    """
    service-tree-migrate command must imply lock, quiet and report
    """
    args = parser.parse_args(["service-tree-migrate"])
    assert args.lock is None
    assert args.quiet
    assert not args.report


def test_subparsers_user_add(parser: argparse.ArgumentParser) -> None:
    """
    user-add command must imply action, architecture, lock, quiet, report and repository
    """
    args = parser.parse_args(["user-add", "username"])
    assert args.action == Action.Update
    assert args.architecture == ""
    assert args.lock is None
    assert args.quiet
    assert not args.report
    assert args.repository == ""


def test_subparsers_user_add_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    user-add command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "user-add", "username"])
    assert args.architecture == ""


def test_subparsers_user_add_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    user-add command must correctly parse repository list
    """
    args = parser.parse_args(["-r", "repo", "user-add", "username"])
    assert args.repository == ""


def test_subparsers_user_add_option_role(parser: argparse.ArgumentParser) -> None:
    """
    user-add command must convert role option to UserAccess instance
    """
    args = parser.parse_args(["user-add", "username"])
    assert isinstance(args.role, UserAccess)
    args = parser.parse_args(["user-add", "username", "--role", "full"])
    assert isinstance(args.role, UserAccess)


def test_subparsers_user_list(parser: argparse.ArgumentParser) -> None:
    """
    user-list command must imply action, architecture, lock, quiet, report, repository and unsafe
    """
    args = parser.parse_args(["user-list"])
    assert args.action == Action.List
    assert args.architecture == ""
    assert args.lock is None
    assert args.quiet
    assert not args.report
    assert args.repository == ""
    assert args.unsafe


def test_subparsers_user_list_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    user-list command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "user-list"])
    assert args.architecture == ""


def test_subparsers_user_list_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    user-list command must correctly parse repository list
    """
    args = parser.parse_args(["-r", "repo", "user-list"])
    assert args.repository == ""


def test_subparsers_user_list_option_role(parser: argparse.ArgumentParser) -> None:
    """
    user-list command must convert role option to UserAccess instance
    """
    args = parser.parse_args(["user-list", "--role", "full"])
    assert isinstance(args.role, UserAccess)


def test_subparsers_user_remove(parser: argparse.ArgumentParser) -> None:
    """
    user-remove command must imply action, architecture, lock, quiet, report and repository
    """
    args = parser.parse_args(["user-remove", "username"])
    assert args.action == Action.Remove
    assert args.architecture == ""
    assert args.lock is None
    assert args.quiet
    assert not args.report
    assert args.repository == ""


def test_subparsers_user_remove_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    user-remove command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "user-remove", "username"])
    assert args.architecture == ""


def test_subparsers_user_remove_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    user-remove command must correctly parse repository list
    """
    args = parser.parse_args(["-r", "repo", "user-remove", "username"])
    assert args.repository == ""


def test_subparsers_web(parser: argparse.ArgumentParser) -> None:
    """
    web command must imply architecture, report, repository and parser
    """
    args = parser.parse_args(["web"])
    assert args.architecture == ""
    assert not args.report
    assert args.repository == ""
    assert args.parser is not None and args.parser()


def test_subparsers_web_option_architecture(parser: argparse.ArgumentParser) -> None:
    """
    web command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "web"])
    assert args.architecture == ""


def test_subparsers_web_option_repository(parser: argparse.ArgumentParser) -> None:
    """
    web command must correctly parse repository list
    """
    args = parser.parse_args(["-r", "repo", "web"])
    assert args.repository == ""


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    application must be run
    """
    path, repository_id = configuration.check_loaded()

    args.architecture = repository_id.architecture
    args.repository = repository_id.name
    args.configuration = path
    args.command = ""
    args.handler = Handler

    mocker.patch("argparse.ArgumentParser.parse_args", return_value=args)

    assert ahriman.run() == 1


def test_run_without_command(args: argparse.Namespace, mocker: MockerFixture) -> None:
    """
    must show help message if run without commands
    """
    args.command = None
    mocker.patch("argparse.ArgumentParser.parse_args", return_value=args)

    with pytest.raises(SystemExit):
        ahriman.run()
