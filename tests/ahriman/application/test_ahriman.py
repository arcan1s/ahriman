import argparse

from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.application.handlers import Handler
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
    assert len(args.architecture) == 2


def test_subparsers_add(parser: argparse.ArgumentParser) -> None:
    """
    add command must imply empty architectures list
    """
    args = parser.parse_args(["add", "ahriman"])
    assert args.architecture == []


def test_subparsers_check(parser: argparse.ArgumentParser) -> None:
    """
    check command must imply empty architecture list, no-aur, no-manual and dry-run
    """
    args = parser.parse_args(["check"])
    assert args.architecture == []
    assert not args.no_aur
    assert args.no_manual
    assert args.dry_run


def test_subparsers_clean(parser: argparse.ArgumentParser) -> None:
    """
    clean command must imply empty architectures list, unsafe and no-log
    """
    args = parser.parse_args(["clean"])
    assert args.architecture == []
    assert args.no_log
    assert args.unsafe


def test_subparsers_config(parser: argparse.ArgumentParser) -> None:
    """
    config command must imply lock, no-log, no-report and unsafe
    """
    args = parser.parse_args(["config"])
    assert args.lock is None
    assert args.no_log
    assert args.no_report
    assert args.unsafe


def test_subparsers_create_user(parser: argparse.ArgumentParser) -> None:
    """
    create-user command must imply architecture, lock, no-log, no-report and unsafe
    """
    args = parser.parse_args(["create-user", "username"])
    assert args.architecture == [""]
    assert args.lock is None
    assert args.no_log
    assert args.no_report
    assert args.unsafe


def test_subparsers_create_user_option_role(parser: argparse.ArgumentParser) -> None:
    """
    create-user command must convert role option to useraccess instance
    """
    args = parser.parse_args(["create-user", "username"])
    assert isinstance(args.role, UserAccess)
    args = parser.parse_args(["create-user", "username", "--role", "write"])
    assert isinstance(args.role, UserAccess)


def test_subparsers_init(parser: argparse.ArgumentParser) -> None:
    """
    init command must imply no_report
    """
    args = parser.parse_args(["init"])
    assert args.no_report


def test_subparsers_key_import(parser: argparse.ArgumentParser) -> None:
    """
    key-import command must imply architecture list, lock and no-report
    """
    args = parser.parse_args(["key-import", "key"])
    assert args.architecture == [""]
    assert args.lock is None
    assert args.no_report


def test_subparsers_rebuild(parser: argparse.ArgumentParser) -> None:
    """
    rebuild command must imply empty architectures list
    """
    args = parser.parse_args(["rebuild"])
    assert args.architecture == []


def test_subparsers_remove(parser: argparse.ArgumentParser) -> None:
    """
    remove command must imply empty architectures list
    """
    args = parser.parse_args(["remove", "ahriman"])
    assert args.architecture == []


def test_subparsers_remove_unknown(parser: argparse.ArgumentParser) -> None:
    """
    remove-unknown command must imply empty architectures list
    """
    args = parser.parse_args(["remove-unknown"])
    assert args.architecture == []


def test_subparsers_report(parser: argparse.ArgumentParser) -> None:
    """
    report command must imply empty architectures list
    """
    args = parser.parse_args(["report"])
    assert args.architecture == []


def test_subparsers_search(parser: argparse.ArgumentParser) -> None:
    """
    search command must imply architecture list, lock, no-log, no-report and unsafe
    """
    args = parser.parse_args(["search", "ahriman"])
    assert args.architecture == [""]
    assert args.lock is None
    assert args.no_log
    assert args.no_report
    assert args.unsafe


def test_subparsers_setup(parser: argparse.ArgumentParser) -> None:
    """
    setup command must imply lock, no-log, no-report and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "setup", "--packager", "John Doe <john@doe.com>",
                              "--repository", "aur-clone"])
    assert args.lock is None
    assert args.no_log
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


def test_subparsers_sign(parser: argparse.ArgumentParser) -> None:
    """
    sign command must imply empty architectures list
    """
    args = parser.parse_args(["sign"])
    assert args.architecture == []


def test_subparsers_status(parser: argparse.ArgumentParser) -> None:
    """
    status command must imply lock, no-log, no-report and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "status"])
    assert args.lock is None
    assert args.no_log
    assert args.no_report
    assert args.unsafe


def test_subparsers_status_update(parser: argparse.ArgumentParser) -> None:
    """
    status-update command must imply lock, no-log, no-report and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "status-update"])
    assert args.lock is None
    assert args.no_log
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


def test_subparsers_sync(parser: argparse.ArgumentParser) -> None:
    """
    sync command must imply empty architectures list
    """
    args = parser.parse_args(["sync"])
    assert args.architecture == []


def test_subparsers_update(parser: argparse.ArgumentParser) -> None:
    """
    update command must imply empty architectures list
    """
    args = parser.parse_args(["update"])
    assert args.architecture == []


def test_subparsers_web(parser: argparse.ArgumentParser) -> None:
    """
    web command must imply lock, no_report and parser
    """
    args = parser.parse_args(["-a", "x86_64", "web"])
    assert args.lock is None
    assert args.no_report
    assert args.parser == parser


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
