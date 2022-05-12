import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers import Triggers
from ahriman.core.configuration import Configuration
from ahriman.models.package import Package
from ahriman.models.result import Result


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
        args(argparse.Namespace): command line arguments fixture

    Returns:
        argparse.Namespace: generated arguments for these test cases
    """
    args.trigger = []
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    application_mock = mocker.patch("ahriman.core.repository.Repository.process_triggers")

    Triggers.run(args, "x86_64", configuration, True, False)
    application_mock.assert_called_once_with(Result())


def test_run_trigger(args: argparse.Namespace, configuration: Configuration, package_ahriman: Package,
                     mocker: MockerFixture) -> None:
    """
    must run triggers specified by command line
    """
    args = _default_args(args)
    args.trigger = ["ahriman.core.report.ReportTrigger"]
    mocker.patch("ahriman.core.repository.Repository.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    report_mock = mocker.patch("ahriman.core.report.ReportTrigger.run")
    upload_mock = mocker.patch("ahriman.core.upload.UploadTrigger.run")

    Triggers.run(args, "x86_64", configuration, True, False)
    report_mock.assert_called_once_with(Result(), [package_ahriman])
    upload_mock.assert_not_called()
