import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers import StatusUpdate
from ahriman.core.configuration import Configuration
from ahriman.models.action import Action
from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.package import Package


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
        args(argparse.Namespace): command line arguments fixture

    Returns:
        argparse.Namespace: generated arguments for these test cases
    """
    args.package = None
    args.action = Action.Update
    args.status = BuildStatusEnum.Success
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    update_self_mock = mocker.patch("ahriman.core.status.client.Client.update_self")

    StatusUpdate.run(args, "x86_64", configuration, report=False, unsafe=False)
    update_self_mock.assert_called_once_with(args.status)


def test_run_packages(args: argparse.Namespace, configuration: Configuration, package_ahriman: Package,
                      mocker: MockerFixture) -> None:
    """
    must run command with specified packages
    """
    args = _default_args(args)
    args.package = [package_ahriman.base]
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    update_mock = mocker.patch("ahriman.core.status.client.Client.update")

    StatusUpdate.run(args, "x86_64", configuration, report=False, unsafe=False)
    update_mock.assert_called_once_with(package_ahriman.base, args.status)


def test_run_remove(args: argparse.Namespace, configuration: Configuration, package_ahriman: Package,
                    mocker: MockerFixture) -> None:
    """
    must remove package from status page
    """
    args = _default_args(args)
    args.package = [package_ahriman.base]
    args.action = Action.Remove
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    update_mock = mocker.patch("ahriman.core.status.client.Client.remove")

    StatusUpdate.run(args, "x86_64", configuration, report=False, unsafe=False)
    update_mock.assert_called_once_with(package_ahriman.base)


def test_imply_with_report(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must create application object with native reporting
    """
    args = _default_args(args)
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    load_mock = mocker.patch("ahriman.core.status.client.Client.load")

    StatusUpdate.run(args, "x86_64", configuration, report=False, unsafe=False)
    load_mock.assert_called_once_with(configuration, report=True)


def test_disallow_auto_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not StatusUpdate.ALLOW_AUTO_ARCHITECTURE_RUN
