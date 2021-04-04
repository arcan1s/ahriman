import argparse

from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.application.handlers import Handler
from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.sign_settings import SignSettings


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
    args = parser.parse_args(["-a", "x86_64", "update"])
    assert isinstance(args.lock, Path)
    args = parser.parse_args(["-a", "x86_64", "-l", "ahriman.lock", "update"])
    assert isinstance(args.lock, Path)


def test_multiple_architectures(parser: argparse.ArgumentParser) -> None:
    """
    must accept multiple architectures
    """
    args = parser.parse_args(["-a", "x86_64", "-a", "i686", "config"])
    assert len(args.architecture) == 2


def test_subparsers_check(parser: argparse.ArgumentParser) -> None:
    """
    check command must imply no_aur, no_manual and dry_run
    """
    args = parser.parse_args(["-a", "x86_64", "check"])
    assert not args.no_aur
    assert args.no_manual
    assert args.dry_run


def test_subparsers_clean(parser: argparse.ArgumentParser) -> None:
    """
    clean command must imply unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "clean"])
    assert args.unsafe


def test_subparsers_config(parser: argparse.ArgumentParser) -> None:
    """
    config command must imply lock, no_report and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "config"])
    assert args.lock is None
    assert args.no_report
    assert args.unsafe


def test_subparsers_setup(parser: argparse.ArgumentParser) -> None:
    """
    setup command must imply lock, no_report and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "setup", "--packager", "John Doe <john@doe.com>",
                              "--repository", "aur-clone"])
    assert args.lock is None
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


def test_subparsers_status(parser: argparse.ArgumentParser) -> None:
    """
    status command must imply lock, no_report and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "status"])
    assert args.lock is None
    assert args.no_report
    assert args.unsafe


def test_subparsers_status_update(parser: argparse.ArgumentParser) -> None:
    """
    status-update command must imply lock, no_report and unsafe
    """
    args = parser.parse_args(["-a", "x86_64", "status-update"])
    assert args.lock is None
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


def test_subparsers_web(parser: argparse.ArgumentParser) -> None:
    """
    web command must imply lock and no_report
    """
    args = parser.parse_args(["-a", "x86_64", "web"])
    assert args.lock is None
    assert args.no_report


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
