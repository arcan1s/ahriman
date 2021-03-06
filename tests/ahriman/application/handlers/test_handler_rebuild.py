import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers import Rebuild
from ahriman.core.configuration import Configuration
from ahriman.models.package import Package


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    args.depends_on = []
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("pathlib.Path.mkdir")
    application_packages_mock = mocker.patch("ahriman.core.repository.repository.Repository.packages")
    application_mock = mocker.patch("ahriman.application.application.Application.update")

    Rebuild.run(args, "x86_64", configuration)
    application_packages_mock.assert_called_once()
    application_mock.assert_called_once()


def test_run_filter(args: argparse.Namespace, configuration: Configuration,
                    package_ahriman: Package, package_python_schedule: Package,
                    mocker: MockerFixture) -> None:
    """
    must run command with depends filter
    """
    args = _default_args(args)
    args.depends_on = ["python-aur"]
    mocker.patch("pathlib.Path.mkdir")
    mocker.patch("ahriman.core.repository.repository.Repository.packages",
                 return_value=[package_ahriman, package_python_schedule])
    application_mock = mocker.patch("ahriman.application.application.Application.update")

    Rebuild.run(args, "x86_64", configuration)
    application_mock.assert_called_with([package_ahriman])


def test_run_without_filter(args: argparse.Namespace, configuration: Configuration,
                            package_ahriman: Package, package_python_schedule: Package,
                            mocker: MockerFixture) -> None:
    """
    must run command for all packages if no filter supplied
    """
    args = _default_args(args)
    mocker.patch("pathlib.Path.mkdir")
    mocker.patch("ahriman.core.repository.repository.Repository.packages",
                 return_value=[package_ahriman, package_python_schedule])
    application_mock = mocker.patch("ahriman.application.application.Application.update")

    Rebuild.run(args, "x86_64", configuration)
    application_mock.assert_called_with([package_ahriman, package_python_schedule])
