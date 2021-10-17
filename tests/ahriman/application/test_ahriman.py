import argparse

from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.application.handlers import Handler
from ahriman.models.action import Action
from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.sign_settings import SignSettings
from ahriman.models.user_access import UserAccess


def test_parser(parser: argparse.ArgumentParser) -> None:
    """
    must parse valid command line
    """
    parser.parse_args(["-a", "x86_64", "repo-config"])


def test_parser_option_configuration(parser: argparse.ArgumentParser) -> None:
    """
    must convert configuration option to Path instance
    """
    args = parser.parse_args(["-a", "x86_64", "repo-config"])
    assert isinstance(args.configuration, Path)
    args = parser.parse_args(["-a", "x86_64", "-c", "ahriman.ini", "repo-config"])
    assert isinstance(args.configuration, Path)


def test_parser_option_lock(parser: argparse.ArgumentParser) -> None:
    """
    must convert lock option to Path instance
    """
    args = parser.parse_args(["repo-update"])
    assert isinstance(args.lock, Path)
    args = parser.parse_args(["-l", "ahriman.lock", "repo-update"])
    assert isinstance(args.lock, Path)


def test_multiple_architectures(parser: argparse.ArgumentParser) -> None:
    """
    must accept multiple architectures
    """
    args = parser.parse_args(["-a", "x86_64", "-a", "i686", "repo-config"])
    assert args.architecture == ["x86_64", "i686"]


def test_subparsers_aur_search(parser: argparse.ArgumentParser) -> None:
    """
    aur-search command must imply architecture list, lock, no-report, quiet and unsafe
    """
    args = parser.parse_args(["aur-search", "ahriman"])
    assert args.architecture == [""]
    assert args.lock is None
    assert args.no_report
    assert args.quiet
    assert args.unsafe


def test_subparsers_aur_search_architecture(parser: argparse.ArgumentParser) -> None:
    """
    aur-search command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "aur-search", "ahriman"])
    assert args.architecture == [""]


def test_subparsers_key_import(parser: argparse.ArgumentParser) -> None:
    """
    key-import command must imply architecture list, lock and no-report
    """
    args = parser.parse_args(["key-import", "key"])
    assert args.architecture == [""]
    assert args.lock is None
    assert args.no_report


def test_subparsers_key_import_architecture(parser: argparse.ArgumentParser) -> None:
    """
    key-import command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "key-import", "key"])
    assert args.architecture == [""]


def test_subparsers_package_add_architecture(parser: argparse.ArgumentParser) -> None:
    """
    package-add command must correctly parse architecture list
    """
    args = parser.parse_args(["package-add", "ahriman"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "package-add", "ahriman"])
    assert args.architecture == ["x86_64"]


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
    package-status command must imply lock, no-report, quiet and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "package-status"])
    assert args.architecture == ["x86_64"]
    assert args.lock is None
    assert args.no_report
    assert args.quiet
    assert args.unsafe


def test_subparsers_package_status_remove(parser: argparse.ArgumentParser) -> None:
    """
    package-status-remove command must imply action, lock, no-report, quiet and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "package-status-remove", "ahriman"])
    assert args.architecture == ["x86_64"]
    assert args.action == Action.Remove
    assert args.lock is None
    assert args.no_report
    assert args.quiet
    assert args.unsafe


def test_subparsers_package_status_update(parser: argparse.ArgumentParser) -> None:
    """
    package-status-update command must imply action, lock, no-report, quiet and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "package-status-update"])
    assert args.architecture == ["x86_64"]
    assert args.action == Action.Update
    assert args.lock is None
    assert args.no_report
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
    patch-add command must imply action, architecture list, lock and no-report
    """
    args = parser.parse_args(["patch-add", "ahriman"])
    assert args.action == Action.Update
    assert args.architecture == [""]
    assert args.lock is None
    assert args.no_report


def test_subparsers_patch_add_architecture(parser: argparse.ArgumentParser) -> None:
    """
    patch-add command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "patch-add", "ahriman"])
    assert args.architecture == [""]


def test_subparsers_patch_add_track(parser: argparse.ArgumentParser) -> None:
    """
    patch-add command must correctly parse track files patterns
    """
    args = parser.parse_args(["patch-add", "-t", "*.py", "ahriman"])
    assert args.track == ["*.diff", "*.patch", "*.py"]


def test_subparsers_patch_list(parser: argparse.ArgumentParser) -> None:
    """
    patch-list command must imply action, architecture list, lock and no-report
    """
    args = parser.parse_args(["patch-list", "ahriman"])
    assert args.action == Action.List
    assert args.architecture == [""]
    assert args.lock is None
    assert args.no_report


def test_subparsers_patch_list_architecture(parser: argparse.ArgumentParser) -> None:
    """
    patch-list command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "patch-list", "ahriman"])
    assert args.architecture == [""]


def test_subparsers_patch_remove(parser: argparse.ArgumentParser) -> None:
    """
    patch-remove command must imply action, architecture list, lock and no-report
    """
    args = parser.parse_args(["patch-remove", "ahriman"])
    assert args.action == Action.Remove
    assert args.architecture == [""]
    assert args.lock is None
    assert args.no_report


def test_subparsers_patch_remove_architecture(parser: argparse.ArgumentParser) -> None:
    """
    patch-remove command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "patch-remove", "ahriman"])
    assert args.architecture == [""]


def test_subparsers_repo_check(parser: argparse.ArgumentParser) -> None:
    """
    repo-check command must imply dry-run, no-aur and no-manual
    """
    args = parser.parse_args(["repo-check"])
    assert args.dry_run
    assert not args.no_aur
    assert args.no_manual


def test_subparsers_repo_check_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-check command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-check"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "repo-check"])
    assert args.architecture == ["x86_64"]


def test_subparsers_repo_clean(parser: argparse.ArgumentParser) -> None:
    """
    repo-clean command must imply quiet and unsafe
    """
    args = parser.parse_args(["repo-clean"])
    assert args.quiet
    assert args.unsafe


def test_subparsers_repo_clean_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-clean command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-clean"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "repo-clean"])
    assert args.architecture == ["x86_64"]


def test_subparsers_repo_config(parser: argparse.ArgumentParser) -> None:
    """
    repo-config command must imply lock, no-report, quiet and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "repo-config"])
    assert args.architecture == ["x86_64"]
    assert args.lock is None
    assert args.no_report
    assert args.quiet
    assert args.unsafe


def test_subparsers_repo_init(parser: argparse.ArgumentParser) -> None:
    """
    repo-init command must imply no_report
    """
    args = parser.parse_args(["-a", "x86_64", "repo-init"])
    assert args.architecture == ["x86_64"]
    assert args.no_report


def test_subparsers_repo_rebuild_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-rebuild command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-rebuild"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "repo-rebuild"])
    assert args.architecture == ["x86_64"]


def test_subparsers_repo_remove_unknown_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-remove-unknown command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-remove-unknown"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "repo-remove-unknown"])
    assert args.architecture == ["x86_64"]


def test_subparsers_repo_report_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-report command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-report"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "repo-report"])
    assert args.architecture == ["x86_64"]


def test_subparsers_repo_setup(parser: argparse.ArgumentParser) -> None:
    """
    repo-setup command must imply lock, no-report, quiet and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "repo-setup", "--packager", "John Doe <john@doe.com>",
                              "--repository", "aur-clone"])
    assert args.architecture == ["x86_64"]
    assert args.lock is None
    assert args.no_report
    assert args.quiet
    assert args.unsafe


def test_subparsers_repo_setup_option_from_configuration(parser: argparse.ArgumentParser) -> None:
    """
    repo-setup command must convert from-configuration option to path instance
    """
    args = parser.parse_args(["-a", "x86_64", "repo-setup", "--packager", "John Doe <john@doe.com>",
                              "--repository", "aur-clone"])
    assert isinstance(args.from_configuration, Path)
    args = parser.parse_args(["-a", "x86_64", "repo-setup", "--packager", "John Doe <john@doe.com>",
                              "--repository", "aur-clone", "--from-configuration", "path"])
    assert isinstance(args.from_configuration, Path)


def test_subparsers_repo_setup_option_sign_target(parser: argparse.ArgumentParser) -> None:
    """
    repo-setup command must convert sign-target option to signsettings instance
    """
    args = parser.parse_args(["-a", "x86_64", "repo-setup", "--packager", "John Doe <john@doe.com>",
                              "--repository", "aur-clone", "--sign-target", "packages"])
    assert args.sign_target
    assert all(isinstance(target, SignSettings) for target in args.sign_target)


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
    re[p-status-update command must imply action, lock, no-report, package, quiet and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "package-status-update"])
    assert args.architecture == ["x86_64"]
    assert args.action == Action.Update
    assert args.lock is None
    assert args.no_report
    assert not args.package
    assert args.quiet
    assert args.unsafe


def test_subparsers_repo_status_update_option_status(parser: argparse.ArgumentParser) -> None:
    """
    repo-status-update command must convert status option to buildstatusenum instance
    """
    args = parser.parse_args(["-a", "x86_64", "repo-status-update"])
    assert isinstance(args.status, BuildStatusEnum)
    args = parser.parse_args(["-a", "x86_64", "repo-status-update", "--status", "failed"])
    assert isinstance(args.status, BuildStatusEnum)


def test_subparsers_repo_sync_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-sync command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-sync"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "repo-sync"])
    assert args.architecture == ["x86_64"]


def test_subparsers_repo_update_architecture(parser: argparse.ArgumentParser) -> None:
    """
    repo-update command must correctly parse architecture list
    """
    args = parser.parse_args(["repo-update"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "repo-update"])
    assert args.architecture == ["x86_64"]


def test_subparsers_user_add(parser: argparse.ArgumentParser) -> None:
    """
    user-add command must imply action, architecture, lock, no-report, quiet and unsafe
    """
    args = parser.parse_args(["user-add", "username"])
    assert args.action == Action.Update
    assert args.architecture == [""]
    assert args.lock is None
    assert args.no_report
    assert args.quiet
    assert args.unsafe


def test_subparsers_user_add_architecture(parser: argparse.ArgumentParser) -> None:
    """
    user-add command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "user-add", "username"])
    assert args.architecture == [""]


def test_subparsers_user_add_option_role(parser: argparse.ArgumentParser) -> None:
    """
    user-add command must convert role option to useraccess instance
    """
    args = parser.parse_args(["user-add", "username"])
    assert isinstance(args.role, UserAccess)
    args = parser.parse_args(["user-add", "username", "--role", "write"])
    assert isinstance(args.role, UserAccess)


def test_subparsers_user_remove(parser: argparse.ArgumentParser) -> None:
    """
    user-remove command must imply action, architecture, lock, no-report, password, quiet, role and unsafe
    """
    args = parser.parse_args(["user-remove", "username"])
    assert args.action == Action.Remove
    assert args.architecture == [""]
    assert args.lock is None
    assert args.no_report
    assert args.password is not None
    assert args.quiet
    assert args.role is not None
    assert args.unsafe


def test_subparsers_user_remove_architecture(parser: argparse.ArgumentParser) -> None:
    """
    user-remove command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "user-remove", "username"])
    assert args.architecture == [""]


def test_subparsers_web(parser: argparse.ArgumentParser) -> None:
    """
    web command must imply lock, no_report and parser
    """
    args = parser.parse_args(["-a", "x86_64", "web"])
    assert args.architecture == ["x86_64"]
    assert args.lock is None
    assert args.no_report
    assert args.parser is not None and args.parser()


def test_run(args: argparse.Namespace, mocker: MockerFixture) -> None:
    """
    application must be run
    """
    args.architecture = "x86_64"
    args.handler = Handler

    from ahriman.application import ahriman
    mocker.patch.object(ahriman, "__name__", "__main__")
    mocker.patch("argparse.ArgumentParser.parse_args", return_value=args)
    exit_mock = mocker.patch("sys.exit")

    ahriman.run()
    exit_mock.assert_called_once()
