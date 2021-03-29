import argparse


def test_parser(parser: argparse.ArgumentParser) -> None:
    """
    must parse valid command line
    """
    parser.parse_args(["-a", "x86_64", "config"])


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
    args = parser.parse_args(["-a", "x86_64", "setup", "--packager", "John Doe <john@doe.com>"])
    assert args.lock is None
    assert args.no_report
    assert args.unsafe


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


def test_subparsers_web(parser: argparse.ArgumentParser) -> None:
    """
    web command must imply lock and no_report
    """
    args = parser.parse_args(["-a", "x86_64", "web"])
    assert args.lock is None
    assert args.no_report
