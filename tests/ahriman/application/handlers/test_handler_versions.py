import argparse

from pytest_mock import MockerFixture
from unittest import mock

from ahriman.application.handlers import Versions
from ahriman.core.configuration import Configuration


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    application_mock = mocker.patch("ahriman.application.handlers.Versions.package_dependencies")
    print_mock = mocker.patch("ahriman.core.formatters.Printer.print")

    Versions.run(args, "x86_64", configuration, True, False)
    application_mock.assert_called_once_with("ahriman", ("pacman", "s3", "web"))
    print_mock.assert_has_calls([mock.call(verbose=False, separator=" "), mock.call(verbose=False, separator=" ")])


def test_package_dependencies() -> None:
    """
    must extract package dependencies
    """
    packages = Versions.package_dependencies("srcinfo")
    assert packages
    assert packages.get("parse") is not None


def test_package_dependencies_missing() -> None:
    """
    must extract package dependencies even if some of them are missing
    """
    packages = Versions.package_dependencies("ahriman", ("docs", "pacman", "s3", "web"))
    assert packages
    assert packages.get("pyalpm") is not None
    assert packages.get("Sphinx") is None
