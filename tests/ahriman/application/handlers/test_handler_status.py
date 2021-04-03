import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers import Status
from ahriman.core.configuration import Configuration
from ahriman.models.build_status import BuildStatus
from ahriman.models.package import Package


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    args.ahriman = True
    args.package = []
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, package_ahriman: Package,
             mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("pathlib.Path.mkdir")
    application_mock = mocker.patch("ahriman.core.status.client.Client.get_self")
    packages_mock = mocker.patch("ahriman.core.status.client.Client.get",
                                 return_value=[(package_ahriman, BuildStatus())])

    Status.run(args, "x86_64", configuration)
    application_mock.assert_called_once()
    packages_mock.assert_called_once()


def test_run_with_package_filter(args: argparse.Namespace, configuration: Configuration, package_ahriman: Package,
                                 mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    args.package = [package_ahriman.base]
    mocker.patch("pathlib.Path.mkdir")
    packages_mock = mocker.patch("ahriman.core.status.client.Client.get",
                                 return_value=[(package_ahriman, BuildStatus())])

    Status.run(args, "x86_64", configuration)
    packages_mock.assert_called_once()

