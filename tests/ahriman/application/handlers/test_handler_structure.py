import argparse
import pytest

from pytest_mock import MockerFixture

from ahriman.application.handlers import Structure
from ahriman.core.configuration import Configuration
from ahriman.core.repository import Repository
from ahriman.models.package import Package


def test_run(args: argparse.Namespace, configuration: Configuration, repository: Repository,
             package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must run command
    """
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    mocker.patch("ahriman.core.repository.Repository.packages", return_value=[package_ahriman])
    application_mock = mocker.patch("ahriman.core.tree.Tree.resolve", return_value=[[package_ahriman]])
    print_mock = mocker.patch("ahriman.core.formatters.Printer.print")

    Structure.run(args, "x86_64", configuration, report=False, unsafe=False)
    application_mock.assert_called_once_with([package_ahriman], repository.paths, pytest.helpers.anyvar(int))
    print_mock.assert_called_once_with(verbose=True, separator=" ")


def test_disallow_auto_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not Structure.ALLOW_AUTO_ARCHITECTURE_RUN
