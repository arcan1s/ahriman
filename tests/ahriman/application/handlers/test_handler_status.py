import argparse

from pytest_mock import MockerFixture
from unittest import mock

from ahriman.application.handlers import Status
from ahriman.core.configuration import Configuration
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.package import Package


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
      args(argparse.Namespace): command line arguments fixture

    Returns:
      argparse.Namespace: generated arguments for these test cases
    """
    args.ahriman = True
    args.exit_code = False
    args.info = False
    args.package = []
    args.status = None
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, package_ahriman: Package,
             package_python_schedule: Package, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    application_mock = mocker.patch("ahriman.core.status.client.Client.get_self")
    packages_mock = mocker.patch("ahriman.core.status.client.Client.get",
                                 return_value=[(package_ahriman, BuildStatus(BuildStatusEnum.Success)),
                                               (package_python_schedule, BuildStatus(BuildStatusEnum.Failed))])
    check_mock = mocker.patch("ahriman.application.handlers.handler.Handler.check_if_empty")
    print_mock = mocker.patch("ahriman.core.formatters.printer.Printer.print")

    Status.run(args, "x86_64", configuration, True, False)
    application_mock.assert_called_once_with()
    packages_mock.assert_called_once_with(None)
    check_mock.assert_called_once_with(False, False)
    print_mock.assert_has_calls([mock.call(False) for _ in range(3)])


def test_run_empty_exception(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must raise ExitCode exception on empty status result
    """
    args = _default_args(args)
    args.exit_code = True
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    mocker.patch("ahriman.core.status.client.Client.get_self")
    mocker.patch("ahriman.core.status.client.Client.get", return_value=[])
    check_mock = mocker.patch("ahriman.application.handlers.handler.Handler.check_if_empty")

    Status.run(args, "x86_64", configuration, True, False)
    check_mock.assert_called_once_with(True, True)


def test_run_verbose(args: argparse.Namespace, configuration: Configuration, package_ahriman: Package,
                     mocker: MockerFixture) -> None:
    """
    must run command with detailed info
    """
    args = _default_args(args)
    args.info = True
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    mocker.patch("ahriman.core.status.client.Client.get",
                 return_value=[(package_ahriman, BuildStatus(BuildStatusEnum.Success))])
    print_mock = mocker.patch("ahriman.core.formatters.printer.Printer.print")

    Status.run(args, "x86_64", configuration, True, False)
    print_mock.assert_has_calls([mock.call(True) for _ in range(2)])


def test_run_with_package_filter(args: argparse.Namespace, configuration: Configuration, package_ahriman: Package,
                                 mocker: MockerFixture) -> None:
    """
    must run command with package filter
    """
    args = _default_args(args)
    args.package = [package_ahriman.base]
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    packages_mock = mocker.patch("ahriman.core.status.client.Client.get",
                                 return_value=[(package_ahriman, BuildStatus(BuildStatusEnum.Success))])

    Status.run(args, "x86_64", configuration, True, False)
    packages_mock.assert_called_once_with(package_ahriman.base)


def test_run_by_status(args: argparse.Namespace, configuration: Configuration, package_ahriman: Package,
                       package_python_schedule: Package, mocker: MockerFixture) -> None:
    """
    must filter packages by status
    """
    args = _default_args(args)
    args.status = BuildStatusEnum.Failed
    mocker.patch("ahriman.core.status.client.Client.get",
                 return_value=[(package_ahriman, BuildStatus(BuildStatusEnum.Success)),
                               (package_python_schedule, BuildStatus(BuildStatusEnum.Failed))])
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    print_mock = mocker.patch("ahriman.core.formatters.printer.Printer.print")

    Status.run(args, "x86_64", configuration, True, False)
    print_mock.assert_has_calls([mock.call(False) for _ in range(2)])


def test_imply_with_report(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must create application object with native reporting
    """
    args = _default_args(args)
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    load_mock = mocker.patch("ahriman.core.status.client.Client.load")

    Status.run(args, "x86_64", configuration, True, False)
    load_mock.assert_called_once_with(configuration)


def test_disallow_auto_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not Status.ALLOW_AUTO_ARCHITECTURE_RUN
