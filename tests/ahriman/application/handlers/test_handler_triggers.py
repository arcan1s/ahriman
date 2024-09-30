import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers.triggers import Triggers
from ahriman.core.configuration import Configuration
from ahriman.core.repository import Repository
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


def test_run(args: argparse.Namespace, configuration: Configuration, repository: Repository,
             mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    application_mock = mocker.patch("ahriman.application.application.Application.on_result")
    on_start_mock = mocker.patch("ahriman.application.application.Application.on_start")

    _, repository_id = configuration.check_loaded()
    Triggers.run(args, repository_id, configuration, report=False)
    application_mock.assert_called_once_with(Result())
    on_start_mock.assert_called_once_with()


def test_run_trigger(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                     package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must run triggers specified by command line
    """
    args = _default_args(args)
    args.trigger = ["ahriman.core.report.ReportTrigger"]
    mocker.patch("ahriman.core.repository.Repository.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    report_mock = mocker.patch("ahriman.core.report.ReportTrigger.on_result")
    upload_mock = mocker.patch("ahriman.core.upload.UploadTrigger.on_result")

    _, repository_id = configuration.check_loaded()
    Triggers.run(args, repository_id, configuration, report=False)
    report_mock.assert_called_once_with(Result(), [package_ahriman])
    upload_mock.assert_not_called()
