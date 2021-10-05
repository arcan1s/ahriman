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
    parser.parse_args(["-a", "x86_64", "config"])


def test_parser_option_configuration(parser: argparse.ArgumentParser) -> None:
    """
    must convert configuration option to Path instance
    """
    args = parser.parse_args(["-a", "x86_64", "config"])
    assert isinstance(args.configuration, Path)
    args = parser.parse_args(["-a", "x86_64", "-c", "ahriman.ini", "config"])
    assert isinstance(args.configuration, Path)


def test_parser_option_lock(parser: argparse.ArgumentParser) -> None:
    """
    must convert lock option to Path instance
    """
    args = parser.parse_args(["update"])
    assert isinstance(args.lock, Path)
    args = parser.parse_args(["-l", "ahriman.lock", "update"])
    assert isinstance(args.lock, Path)


def test_multiple_architectures(parser: argparse.ArgumentParser) -> None:
    """
    must accept multiple architectures
    """
    args = parser.parse_args(["-a", "x86_64", "-a", "i686", "config"])
    assert args.architecture == ["x86_64", "i686"]


def test_subparsers_add_architecture(parser: argparse.ArgumentParser) -> None:
    """
    add command must correctly parse architecture list
    """
    args = parser.parse_args(["add", "ahriman"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "add", "ahriman"])
    assert args.architecture == ["x86_64"]


def test_subparsers_check(parser: argparse.ArgumentParser) -> None:
    """
    check command must imply no-aur, no-manual and dry-run
    """
    args = parser.parse_args(["check"])
    assert not args.no_aur
    assert args.no_manual
    assert args.dry_run


def test_subparsers_check_architecture(parser: argparse.ArgumentParser) -> None:
    """
    check command must correctly parse architecture list
    """
    args = parser.parse_args(["check"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "check"])
    assert args.architecture == ["x86_64"]


def test_subparsers_clean(parser: argparse.ArgumentParser) -> None:
    """
    clean command must imply unsafe and no-log
    """
    args = parser.parse_args(["clean"])
    assert args.quiet
    assert args.unsafe


def test_subparsers_clean_architecture(parser: argparse.ArgumentParser) -> None:
    """
    clean command must correctly parse architecture list
    """
    args = parser.parse_args(["clean"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "clean"])
    assert args.architecture == ["x86_64"]


def test_subparsers_config(parser: argparse.ArgumentParser) -> None:
    """
    config command must imply lock, no-log, no-report and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "config"])
    assert args.architecture == ["x86_64"]
    assert args.lock is None
    assert args.quiet
    assert args.no_report
    assert args.unsafe


def test_subparsers_init(parser: argparse.ArgumentParser) -> None:
    """
    init command must imply no_report
    """
    args = parser.parse_args(["-a", "x86_64", "init"])
    assert args.architecture == ["x86_64"]
    assert args.no_report


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


def test_subparsers_rebuild_architecture(parser: argparse.ArgumentParser) -> None:
    """
    rebuild command must correctly parse architecture list
    """
    args = parser.parse_args(["rebuild"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "rebuild"])
    assert args.architecture == ["x86_64"]


def test_subparsers_remove_architecture(parser: argparse.ArgumentParser) -> None:
    """
    remove command must correctly parse architecture list
    """
    args = parser.parse_args(["remove", "ahriman"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "remove", "ahriman"])
    assert args.architecture == ["x86_64"]


def test_subparsers_report_architecture(parser: argparse.ArgumentParser) -> None:
    """
    report command must correctly parse architecture list
    """
    args = parser.parse_args(["report"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "report"])
    assert args.architecture == ["x86_64"]


def test_subparsers_search(parser: argparse.ArgumentParser) -> None:
    """
    search command must imply architecture list, lock, no-log, no-report and unsafe
    """
    args = parser.parse_args(["search", "ahriman"])
    assert args.architecture == [""]
    assert args.lock is None
    assert args.quiet
    assert args.no_report
    assert args.unsafe


def test_subparsers_search_architecture(parser: argparse.ArgumentParser) -> None:
    """
    search command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "search", "ahriman"])
    assert args.architecture == [""]


def test_subparsers_setup(parser: argparse.ArgumentParser) -> None:
    """
    setup command must imply lock, no-log, no-report and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "setup", "--packager", "John Doe <john@doe.com>",
                              "--repository", "aur-clone"])
    assert args.architecture == ["x86_64"]
    assert args.lock is None
    assert args.quiet
    assert args.no_report
    assert args.unsafe


def test_subparsers_setup_option_from_configuration(parser: argparse.ArgumentParser) -> None:
    """
    setup command must convert from-configuration option to path instance
    """
    args = parser.parse_args(["-a", "x86_64", "setup", "--packager", "John Doe <john@doe.com>",
                              "--repository", "aur-clone"])
    assert isinstance(args.from_configuration, Path)
    args = parser.parse_args(["-a", "x86_64", "setup", "--packager", "John Doe <john@doe.com>",
                              "--repository", "aur-clone", "--from-configuration", "path"])
    assert isinstance(args.from_configuration, Path)


def test_subparsers_setup_option_sign_target(parser: argparse.ArgumentParser) -> None:
    """
    setup command must convert sign-target option to signsettings instance
    """
    args = parser.parse_args(["-a", "x86_64", "setup", "--packager", "John Doe <john@doe.com>",
                              "--repository", "aur-clone", "--sign-target", "packages"])
    assert args.sign_target
    assert all(isinstance(target, SignSettings) for target in args.sign_target)


def test_subparsers_sign_architecture(parser: argparse.ArgumentParser) -> None:
    """
    sign command must correctly parse architecture list
    """
    args = parser.parse_args(["sign"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "sign"])
    assert args.architecture == ["x86_64"]


def test_subparsers_status(parser: argparse.ArgumentParser) -> None:
    """
    status command must imply lock, no-log, no-report and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "status"])
    assert args.architecture == ["x86_64"]
    assert args.lock is None
    assert args.quiet
    assert args.no_report
    assert args.unsafe


def test_subparsers_status_update(parser: argparse.ArgumentParser) -> None:
    """
    status-update command must imply lock, no-log, no-report and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "status-update"])
    assert args.architecture == ["x86_64"]
    assert args.lock is None
    assert args.quiet
    assert args.no_report
    assert args.unsafe


def test_subparsers_status_update_option_status(parser: argparse.ArgumentParser) -> None:
    """
    status-update command must convert status option to buildstatusenum instance
    """
    args = parser.parse_args(["-a", "x86_64", "status-update"])
    assert isinstance(args.status, BuildStatusEnum)
    args = parser.parse_args(["-a", "x86_64", "status-update", "--status", "failed"])
    assert isinstance(args.status, BuildStatusEnum)


def test_subparsers_sync_architecture(parser: argparse.ArgumentParser) -> None:
    """
    sync command must correctly parse architecture list
    """
    args = parser.parse_args(["sync"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "sync"])
    assert args.architecture == ["x86_64"]


def test_subparsers_update_architecture(parser: argparse.ArgumentParser) -> None:
    """
    update command must correctly parse architecture list
    """
    args = parser.parse_args(["update"])
    assert args.architecture is None
    args = parser.parse_args(["-a", "x86_64", "update"])
    assert args.architecture == ["x86_64"]


def test_subparsers_user(parser: argparse.ArgumentParser) -> None:
    """
    user command must imply architecture, lock, no-log, no-report and unsafe
    """
    args = parser.parse_args(["user", "username"])
    assert args.architecture == [""]
    assert args.lock is None
    assert args.quiet
    assert args.no_report
    assert args.unsafe


def test_subparsers_user_architecture(parser: argparse.ArgumentParser) -> None:
    """
    user command must correctly parse architecture list
    """
    args = parser.parse_args(["-a", "x86_64", "user", "username"])
    assert args.architecture == [""]


def test_subparsers_user_option_role(parser: argparse.ArgumentParser) -> None:
    """
    user command must convert role option to useraccess instance
    """
    args = parser.parse_args(["user", "username"])
    assert isinstance(args.access, UserAccess)
    args = parser.parse_args(["user", "username", "--access", "write"])
    assert isinstance(args.access, UserAccess)


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
