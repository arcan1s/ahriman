import argparse
import pytest

from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.application import ahriman
from ahriman.application.handlers import Handler
from ahriman.models.action import Action
from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.log_handler import LogHandler
from ahriman.models.sign_settings import SignSettings
from ahriman.models.user_access import UserAccess


def test_parser(parser: argparse.ArgumentParser) -> None:
    """
    must parse valid command line
    """
    parser.parse_args(["-a", "x86_64", "service-config"])


def test_parser_option_configuration(parser: argparse.ArgumentParser) -> None:
    """
    must convert configuration option to Path instance
    """
    args = parser.parse_args(["-a", "x86_64", "service-config"])
    assert isinstance(args.configuration, Path)
    args = parser.parse_args(["-a", "x86_64", "-c", "ahriman.ini", "service-config"])
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


def test_multiple_architectures(parser: argparse.ArgumentParser) -> None:
    """
    must accept multiple architectures
    """
    args = parser.parse_args(["-a", "x86_64", "-a", "i686", "service-config"])
    assert args.architecture == ["x86_64", "i686"]


def test_subparsers_aur_search(parser: argparse.ArgumentParser) -> None:
    """
    aur-search command must imply architecture list, lock, report, quiet and unsafe
    """
    args = parser.parse_args(["aur-search", "ahriman"])
    assert args.architecture == [""]
    assert args.lock is None
    assert not args.report
    assert args.quiet
    assert args.unsafe


def test_subparsers_aur_search_architecture(parser: argparse.ArgumentParser) -> None:
    """
    aur-search command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "aur-search", "ahriman"])
    assert args.architecture == [""]


def test_subparsers_help(parser: argparse.ArgumentParser) -> None:
    """
    help command must imply architecture list, lock, report, quiet, unsafe and parser
    """
    args = parser.parse_args(["help"])
    assert args.architecture == [""]
    assert args.lock is None
    assert not args.report
    assert args.quiet
    assert args.unsafe
    assert args.parser is not None and args.parser()


def test_subparsers_help_architecture(parser: argparse.ArgumentParser) -> None:
    """
    help command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "help"])
    assert args.architecture == [""]


def test_subparsers_help_commands_unsafe(parser: argparse.ArgumentParser) -> None:
    """
    help-commands-unsafe command must imply architecture list, lock, report, quiet, unsafe and parser
    """
    args = parser.parse_args(["help-commands-unsafe"])
    assert args.architecture == [""]
    assert args.lock is None
    assert not args.report
    assert args.quiet
    assert args.unsafe
    assert args.parser is not None and args.parser()


def test_subparsers_help_commands_unsafe_architecture(parser: argparse.ArgumentParser) -> None:
    """
    help-commands-unsafe command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "help-commands-unsafe"])
    assert args.architecture == [""]


def test_subparsers_help_updates(parser: argparse.ArgumentParser) -> None:
    """
    help-updates command must imply architecture list, lock, report, quiet and unsafe
    """
    args = parser.parse_args(["help-updates"])
    assert args.architecture == [""]
    assert args.lock is None
    assert not args.report
    assert args.quiet
    assert args.unsafe


def test_subparsers_help_updates_architecture(parser: argparse.ArgumentParser) -> None:
    """
    help-updates command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "help-updates"])
    assert args.architecture == [""]


def test_subparsers_help_version(parser: argparse.ArgumentParser) -> None:
    """
    help-version command must imply architecture, lock, report, quiet and unsafe
    """
    args = parser.parse_args(["help-version"])
    assert args.architecture == [""]
    assert args.lock is None
    assert not args.report
    assert args.quiet
    assert args.unsafe


def test_subparsers_help_version_architecture(parser: argparse.ArgumentParser) -> None:
    """
    help-version command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "help-version"])
    assert args.architecture == [""]


def test_subparsers_package_add_architecture(parser: argparse.ArgumentParser) -> None:
    """
    package-add command must correctly parse architecture list
    """
    args = parser.parse_args(["package-add", "ahriman"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "package-add", "ahriman"])
    assert args.architecture == ["x86_64"]


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


def test_subparsers_package_remove_architecture(parser: argparse.ArgumentParser) -> None:
    """
    package-remove command must correctly parse architecture list
    """
    args = parser.parse_args(["package-remove", "ahriman"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "package-remove", "ahriman"])
    assert args.architecture == ["x86_64"]


def test_subparsers_package_status(parser: argparse.ArgumentParser) -> None:
    """
    package-status command must imply lock, report, quiet and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "package-status"])
    assert args.architecture == ["x86_64"]
    assert args.lock is None
    assert not args.report
    assert args.quiet
    assert args.unsafe


def test_subparsers_package_status_remove(parser: argparse.ArgumentParser) -> None:
    """
    package-status-remove command must imply action, lock, report, quiet and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "package-status-remove", "ahriman"])
    assert args.architecture == ["x86_64"]
    assert args.action == Action.Remove
    assert args.lock is None
    assert not args.report
    assert args.quiet
    assert args.unsafe


def test_subparsers_package_status_update(parser: argparse.ArgumentParser) -> None:
    """
    package-status-update command must imply action, lock, report, quiet and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "package-status-update"])
    assert args.architecture == ["x86_64"]
    assert args.action == Action.Update
    assert args.lock is None
    assert not args.report
    assert args.quiet
    assert args.unsafe


def test_subparsers_package_status_update_option_status(parser: argparse.ArgumentParser) -> None:
    """
    package-status-update command must convert status option to buildstatusenum instance
    """
    args = parser.parse_args(["-a", "x86_64", "package-status-update"])
    assert isinstance(args.status, BuildStatusEnum)
    args = parser.parse_args(["-a", "x86_64", "package-status-update", "--status", "failed"])
    assert isinstance(args.status, BuildStatusEnum)


def test_subparsers_patch_add(parser: argparse.ArgumentParser) -> None:
    """
    patch-add command must imply action, architecture list, lock and report
    """
    args = parser.parse_args(["patch-add", "ahriman", "version"])
    assert args.action == Action.Update
    assert args.architecture == [""]
    assert args.lock is None
    assert not args.report


def test_subparsers_patch_add_architecture(parser: argparse.ArgumentParser) -> None:
    """
    patch-add command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "patch-add", "ahriman", "version"])
    assert args.architecture == [""]


def test_subparsers_patch_list(parser: argparse.ArgumentParser) -> None:
    """
    patch-list command must imply action, architecture list, lock, report and unsafe
    """
    args = parser.parse_args(["patch-list", "ahriman"])
    assert args.action == Action.List
    assert args.architecture == [""]
    assert args.lock is None
    assert not args.report
    assert args.unsafe


def test_subparsers_patch_list_architecture(parser: argparse.ArgumentParser) -> None:
    """
    patch-list command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "patch-list", "ahriman"])
    assert args.architecture == [""]


def test_subparsers_patch_remove(parser: argparse.ArgumentParser) -> None:
    """
    patch-remove command must imply action, architecture list, lock and report
    """
    args = parser.parse_args(["patch-remove", "ahriman"])
    assert args.action == Action.Remove
    assert args.architecture == [""]
    assert args.lock is None
    assert not args.report


def test_subparsers_patch_remove_architecture(parser: argparse.ArgumentParser) -> None:
    """
    patch-remove command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "patch-remove", "ahriman"])
    assert args.architecture == [""]


def test_subparsers_patch_set_add(parser: argparse.ArgumentParser) -> None:
    """
    patch-set-add command must imply action, architecture list, lock, report and variable
    """
    args = parser.parse_args(["patch-set-add", "ahriman"])
    assert args.action == Action.Update
    assert args.architecture == [""]
    assert args.lock is None
    assert not args.report
    assert args.variable is None


def test_subparsers_patch_set_add_architecture(parser: argparse.ArgumentParser) -> None:
    """
    patch-set-add command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "patch-set-add", "ahriman"])
    assert args.architecture == [""]


def test_subparsers_patch_set_add_option_package(parser: argparse.ArgumentParser) -> None:
    """
    patch-set-add command must convert package option to path instance
    """
    args = parser.parse_args(["patch-set-add", "ahriman"])
    assert isinstance(args.package, Path)


def test_subparsers_patch_set_add_option_track(parser: argparse.ArgumentParser) -> None:
    """
    patch-set-add command must correctly parse track files patterns
    """
    args = parser.parse_args(["patch-set-add", "-t", "*.py", "ahriman"])
    assert args.track == ["*.diff", "*.patch", "*.py"]


def test_subparsers_repo_backup(parser: argparse.ArgumentParser) -> None:
    """
    repo-backup command must imply architecture list, lock, report and unsafe
    """
    args = parser.parse_args(["repo-backup", "output.zip"])
    assert args.architecture == [""]
    assert args.lock is None
    assert not args.report
    assert args.unsafe


def test_subparsers_repo_backup_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-backup command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "repo-backup", "output.zip"])
    assert args.architecture == [""]


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


def test_subparsers_repo_check_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-check command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-check"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "repo-check"])
    assert args.architecture == ["x86_64"]


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


def test_subparsers_repo_create_keyring_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-create-keyring command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-create-keyring"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "repo-create-keyring"])
    assert args.architecture == ["x86_64"]


def test_subparsers_repo_create_mirrorlist(parser: argparse.ArgumentParser) -> None:
    """
    repo-create-mirrorlist command must imply trigger
    """
    args = parser.parse_args(["repo-create-mirrorlist"])
    assert args.trigger == ["ahriman.core.support.MirrorlistTrigger"]


def test_subparsers_repo_create_mirrorlist_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-create-mirrorlist command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-create-mirrorlist"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "repo-create-mirrorlist"])
    assert args.architecture == ["x86_64"]


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


def test_subparsers_repo_rebuild_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-rebuild command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-rebuild"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "repo-rebuild"])
    assert args.architecture == ["x86_64"]


def test_subparsers_repo_rebuild_option_status(parser: argparse.ArgumentParser) -> None:
    """
    repo-rebuild command must convert status option to BuildStatusEnum instance
    """
    args = parser.parse_args(["-a", "x86_64", "repo-rebuild", "--status", "failed"])
    assert isinstance(args.status, BuildStatusEnum)


def test_subparsers_repo_remove_unknown_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-remove-unknown command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-remove-unknown"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "repo-remove-unknown"])
    assert args.architecture == ["x86_64"]


def test_subparsers_repo_report(parser: argparse.ArgumentParser) -> None:
    """
    repo-report command must imply trigger
    """
    args = parser.parse_args(["repo-report"])
    assert args.trigger == ["ahriman.core.report.ReportTrigger"]


def test_subparsers_repo_report_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-report command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-report"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "repo-report"])
    assert args.architecture == ["x86_64"]


def test_subparsers_repo_restore(parser: argparse.ArgumentParser) -> None:
    """
    repo-restore command must imply architecture list, lock, report and unsafe
    """
    args = parser.parse_args(["repo-restore", "output.zip"])
    assert args.architecture == [""]
    assert args.lock is None
    assert not args.report
    assert args.unsafe


def test_subparsers_repo_restore_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-restore command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "repo-restore", "output.zip"])
    assert args.architecture == [""]


def test_subparsers_repo_sign_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-sign command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-sign"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "repo-sign"])
    assert args.architecture == ["x86_64"]


def test_subparsers_repo_status_update(parser: argparse.ArgumentParser) -> None:
    """
    re[p-status-update command must imply action, lock, report, package, quiet and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "package-status-update"])
    assert args.architecture == ["x86_64"]
    assert args.action == Action.Update
    assert args.lock is None
    assert not args.report
    assert not args.package
    assert args.quiet
    assert args.unsafe


def test_subparsers_repo_status_update_option_status(parser: argparse.ArgumentParser) -> None:
    """
    repo-status-update command must convert status option to BuildStatusEnum instance
    """
    args = parser.parse_args(["-a", "x86_64", "repo-status-update"])
    assert isinstance(args.status, BuildStatusEnum)
    args = parser.parse_args(["-a", "x86_64", "repo-status-update", "--status", "failed"])
    assert isinstance(args.status, BuildStatusEnum)


def test_subparsers_repo_sync(parser: argparse.ArgumentParser) -> None:
    """
    repo-sync command must imply trigger
    """
    args = parser.parse_args(["repo-sync"])
    assert args.trigger == ["ahriman.core.upload.UploadTrigger"]


def test_subparsers_repo_sync_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-sync command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-sync"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "repo-sync"])
    assert args.architecture == ["x86_64"]


def test_subparsers_repo_tree(parser: argparse.ArgumentParser) -> None:
    """
    repo-tree command must imply lock, report, quiet and unsafe
    """
    args = parser.parse_args(["repo-tree"])
    assert args.lock is None
    assert not args.report
    assert args.quiet
    assert args.unsafe


def test_subparsers_repo_tree_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-tree command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-tree"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "repo-tree"])
    assert args.architecture == ["x86_64"]


def test_subparsers_repo_tree_option_partitions(parser: argparse.ArgumentParser) -> None:
    """
    must convert partitions option to int instance
    """
    args = parser.parse_args(["repo-tree"])
    assert isinstance(args.partitions, int)
    args = parser.parse_args(["repo-tree", "--partitions", "42"])
    assert isinstance(args.partitions, int)


def test_subparsers_repo_triggers_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-triggers command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-triggers"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "repo-triggers"])
    assert args.architecture == ["x86_64"]


def test_subparsers_repo_update_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-update command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-update"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "repo-update"])
    assert args.architecture == ["x86_64"]


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


def test_subparsers_service_clean_architecture(parser: argparse.ArgumentParser) -> None:
    """
    service-clean command must correctly parse architecture list
    """
    args = parser.parse_args(["service-clean"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "service-clean"])
    assert args.architecture == ["x86_64"]


def test_subparsers_service_config(parser: argparse.ArgumentParser) -> None:
    """
    service-config command must imply lock, report, quiet and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "service-config"])
    assert args.architecture == ["x86_64"]
    assert args.lock is None
    assert not args.report
    assert args.quiet
    assert args.unsafe


def test_subparsers_service_config_validate(parser: argparse.ArgumentParser) -> None:
    """
    service-config-validate command must imply lock, report, quiet and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "service-config-validate"])
    assert args.architecture == ["x86_64"]
    assert args.lock is None
    assert not args.report
    assert args.quiet
    assert args.unsafe


def test_subparsers_service_key_import(parser: argparse.ArgumentParser) -> None:
    """
    service-key-import command must imply architecture list, lock and report
    """
    args = parser.parse_args(["service-key-import", "key"])
    assert args.architecture == [""]
    assert args.lock is None
    assert not args.report


def test_subparsers_service_key_import_architecture(parser: argparse.ArgumentParser) -> None:
    """
    service-key-import command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "service-key-import", "key"])
    assert args.architecture == [""]


def test_subparsers_service_setup(parser: argparse.ArgumentParser) -> None:
    """
    service-setup command must imply lock, report, quiet and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "service-setup", "--packager", "John Doe <john@doe.com>",
                              "--repository", "aur-clone"])
    assert args.architecture == ["x86_64"]
    assert args.lock is None
    assert not args.report
    assert args.quiet
    assert args.unsafe


def test_subparsers_service_setup_option_from_configuration(parser: argparse.ArgumentParser) -> None:
    """
    service-setup command must convert from-configuration option to path instance
    """
    args = parser.parse_args(["-a", "x86_64", "service-setup", "--packager", "John Doe <john@doe.com>",
                              "--repository", "aur-clone"])
    assert isinstance(args.from_configuration, Path)
    args = parser.parse_args(["-a", "x86_64", "service-setup", "--packager", "John Doe <john@doe.com>",
                              "--repository", "aur-clone", "--from-configuration", "path"])
    assert isinstance(args.from_configuration, Path)


def test_subparsers_service_setup_option_sign_target(parser: argparse.ArgumentParser) -> None:
    """
    service-setup command must convert sign-target option to SignSettings instance
    """
    args = parser.parse_args(["-a", "x86_64", "service-setup", "--packager", "John Doe <john@doe.com>",
                              "--repository", "aur-clone", "--sign-target", "packages"])
    assert args.sign_target
    assert all(isinstance(target, SignSettings) for target in args.sign_target)


def test_subparsers_service_shell(parser: argparse.ArgumentParser) -> None:
    """
    service-shell command must imply lock and report
    """
    args = parser.parse_args(["service-shell"])
    assert args.lock is None
    assert not args.report


def test_subparsers_user_add(parser: argparse.ArgumentParser) -> None:
    """
    user-add command must imply action, architecture, lock, report and quiet
    """
    args = parser.parse_args(["user-add", "username"])
    assert args.action == Action.Update
    assert args.architecture == [""]
    assert args.lock is None
    assert not args.report
    assert args.quiet


def test_subparsers_user_add_architecture(parser: argparse.ArgumentParser) -> None:
    """
    user-add command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "user-add", "username"])
    assert args.architecture == [""]


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
    user-list command must imply action, architecture, lock, report, quiet and unsafe
    """
    args = parser.parse_args(["user-list"])
    assert args.action == Action.List
    assert args.architecture == [""]
    assert args.lock is None
    assert not args.report
    assert args.quiet
    assert args.unsafe


def test_subparsers_user_list_architecture(parser: argparse.ArgumentParser) -> None:
    """
    user-list command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "user-list"])
    assert args.architecture == [""]


def test_subparsers_user_list_option_role(parser: argparse.ArgumentParser) -> None:
    """
    user-list command must convert role option to UserAccess instance
    """
    args = parser.parse_args(["user-list", "--role", "full"])
    assert isinstance(args.role, UserAccess)


def test_subparsers_user_remove(parser: argparse.ArgumentParser) -> None:
    """
    user-remove command must imply action, architecture, lock, report and quiet
    """
    args = parser.parse_args(["user-remove", "username"])
    assert args.action == Action.Remove
    assert args.architecture == [""]
    assert args.lock is None
    assert not args.report
    assert args.quiet


def test_subparsers_user_remove_architecture(parser: argparse.ArgumentParser) -> None:
    """
    user-remove command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "user-remove", "username"])
    assert args.architecture == [""]


def test_subparsers_web(parser: argparse.ArgumentParser) -> None:
    """
    web command must imply report and parser
    """
    args = parser.parse_args(["-a", "x86_64", "web"])
    assert args.architecture == ["x86_64"]
    assert not args.report
    assert args.parser is not None and args.parser()


def test_run(args: argparse.Namespace, mocker: MockerFixture) -> None:
    """
    application must be run
    """
    args.architecture = "x86_64"
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
