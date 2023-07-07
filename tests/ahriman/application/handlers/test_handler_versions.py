import argparse

from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.application.handlers import Versions
from ahriman.core.configuration import Configuration


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    application_mock = mocker.patch("ahriman.application.handlers.Versions.package_dependencies")
    print_mock = mocker.patch("ahriman.core.formatters.Printer.print")

    Versions.run(args, "x86_64", configuration, report=False)
    application_mock.assert_called_once_with("ahriman")
    print_mock.assert_has_calls([MockCall(verbose=False, separator=" "), MockCall(verbose=False, separator=" ")])


def test_package_dependencies() -> None:
    """
    must extract package dependencies
    """
    packages = dict(Versions.package_dependencies("srcinfo"))
    assert packages
    assert packages.get("parse") is not None


def test_package_dependencies_missing() -> None:
    """
    must extract package dependencies even if some of them are missing
    """
    packages = dict(Versions.package_dependencies("ahriman"))
    assert packages
    assert packages.get("pyalpm") is not None
    assert packages.get("Sphinx") is None
