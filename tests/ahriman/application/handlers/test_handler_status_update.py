import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers import StatusUpdate
from ahriman.core.configuration import Configuration
from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.package import Package


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    args.status = BuildStatusEnum.Success.value
    args.package = None
    args.remove = False
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("pathlib.Path.mkdir")
    update_self_mock = mocker.patch("ahriman.core.status.client.Client.update_self")

    StatusUpdate.run(args, "x86_64", configuration)
    update_self_mock.assert_called_once()


def test_run_packages(args: argparse.Namespace, configuration: Configuration, package_ahriman: Package,
                      mocker: MockerFixture) -> None:
    """
    must run command with specified packages
    """
    args = _default_args(args)
    args.package = [package_ahriman.base]
    mocker.patch("pathlib.Path.mkdir")
    update_mock = mocker.patch("ahriman.core.status.client.Client.update")

    StatusUpdate.run(args, "x86_64", configuration)
    update_mock.assert_called_once()


def test_run_remove(args: argparse.Namespace, configuration: Configuration, package_ahriman: Package,
                    mocker: MockerFixture) -> None:
    """
    must remove package from status page
    """
    args = _default_args(args)
    args.package = [package_ahriman.base]
    args.remove = True
    mocker.patch("pathlib.Path.mkdir")
    update_mock = mocker.patch("ahriman.core.status.client.Client.remove")

    StatusUpdate.run(args, "x86_64", configuration)
    update_mock.assert_called_once()
