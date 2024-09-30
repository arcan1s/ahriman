import argparse
import pytest

from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.application.handlers.versions import Versions
from ahriman.core.configuration import Configuration


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    application_mock = mocker.patch("ahriman.application.handlers.versions.Versions.package_dependencies")
    print_mock = mocker.patch("ahriman.core.formatters.Printer.print")

    _, repository_id = configuration.check_loaded()
    Versions.run(args, repository_id, configuration, report=False)
    application_mock.assert_called_once_with("ahriman")
    print_mock.assert_has_calls([
        MockCall(verbose=False, log_fn=pytest.helpers.anyvar(int), separator=" "),
        MockCall(verbose=False, log_fn=pytest.helpers.anyvar(int), separator=" "),
    ])


def test_package_dependencies() -> None:
    """
    must extract package dependencies
    """
    packages = dict(Versions.package_dependencies("requests"))
    assert packages
    assert packages.get("urllib3") is not None


def test_package_dependencies_missing() -> None:
    """
    must extract package dependencies even if some of them are missing
    """
    packages = dict(Versions.package_dependencies("ahriman"))
    assert packages
    assert packages.get("pyalpm") is not None
    assert packages.get("Sphinx") is None


def test_disallow_multi_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not Versions.ALLOW_MULTI_ARCHITECTURE_RUN
