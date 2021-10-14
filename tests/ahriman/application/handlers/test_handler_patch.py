import argparse

from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.application.application import Application
from ahriman.application.handlers import Patch
from ahriman.core.configuration import Configuration
from ahriman.models.action import Action
from ahriman.models.package import Package


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases
    :param args: command line arguments fixture
    :return: generated arguments for these test cases
    """
    args.package = "ahriman"
    args.remove = False
    args.track = ["*.diff", "*.patch"]
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    args.action = Action.Update
    mocker.patch("pathlib.Path.mkdir")
    application_mock = mocker.patch("ahriman.application.handlers.patch.Patch.patch_set_create")

    Patch.run(args, "x86_64", configuration, True)
    application_mock.assert_called_once()


def test_run_list(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command with list flag
    """
    args = _default_args(args)
    args.action = Action.List
    mocker.patch("pathlib.Path.mkdir")
    application_mock = mocker.patch("ahriman.application.handlers.patch.Patch.patch_set_list")

    Patch.run(args, "x86_64", configuration, True)
    application_mock.assert_called_once()


def test_run_remove(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command with remove flag
    """
    args = _default_args(args)
    args.action = Action.Remove
    mocker.patch("pathlib.Path.mkdir")
    application_mock = mocker.patch("ahriman.application.handlers.patch.Patch.patch_set_remove")

    Patch.run(args, "x86_64", configuration, True)
    application_mock.assert_called_once()


def test_patch_set_list(application: Application, mocker: MockerFixture) -> None:
    """
    must list available patches for the command
    """
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    glob_mock = mocker.patch("pathlib.Path.glob", return_value=[Path("local")])
    print_mock = mocker.patch("ahriman.application.handlers.patch.Patch._print")

    Patch.patch_set_list(application, "ahriman")
    glob_mock.assert_called_once_with("*.patch")
    print_mock.assert_called()


def test_patch_set_list_no_dir(application: Application, mocker: MockerFixture) -> None:
    """
    must not fail if no patches directory found
    """
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    glob_mock = mocker.patch("pathlib.Path.glob")
    print_mock = mocker.patch("ahriman.application.handlers.patch.Patch._print")

    Patch.patch_set_list(application, "ahriman")
    glob_mock.assert_not_called()
    print_mock.assert_not_called()


def test_patch_set_create(application: Application, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must create patch set for the package
    """
    mocker.patch("ahriman.models.package.Package.load", return_value=package_ahriman)
    remove_mock = mocker.patch("ahriman.application.handlers.patch.Patch.patch_set_remove")
    create_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.patch_create")
    patch_dir = application.repository.paths.patches_for(package_ahriman.base)

    Patch.patch_set_create(application, Path("path"), ["*.patch"])
    remove_mock.assert_called_once_with(application, package_ahriman.base)
    create_mock.assert_called_once_with(Path("path"), patch_dir / "00-main.patch", "*.patch")


def test_patch_set_remove(application: Application, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must remove patch set for the package
    """
    remove_mock = mocker.patch("shutil.rmtree")
    patch_dir = application.repository.paths.patches_for(package_ahriman.base)

    Patch.patch_set_remove(application, package_ahriman.base)
    remove_mock.assert_called_once_with(patch_dir, ignore_errors=True)
