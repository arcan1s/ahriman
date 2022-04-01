import argparse
import pytest

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
    args.exit_code = False
    args.remove = False
    args.track = ["*.diff", "*.patch"]
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    args.action = Action.Update
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    application_mock = mocker.patch("ahriman.application.handlers.patch.Patch.patch_set_create")

    Patch.run(args, "x86_64", configuration, True, False)
    application_mock.assert_called_once_with(pytest.helpers.anyvar(int), args.package, args.track)


def test_run_list(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command with list flag
    """
    args = _default_args(args)
    args.action = Action.List
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    application_mock = mocker.patch("ahriman.application.handlers.patch.Patch.patch_set_list")

    Patch.run(args, "x86_64", configuration, True, False)
    application_mock.assert_called_once_with(pytest.helpers.anyvar(int), args.package, False)


def test_run_remove(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command with remove flag
    """
    args = _default_args(args)
    args.action = Action.Remove
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    application_mock = mocker.patch("ahriman.application.handlers.patch.Patch.patch_set_remove")

    Patch.run(args, "x86_64", configuration, True, False)
    application_mock.assert_called_once_with(pytest.helpers.anyvar(int), args.package)


def test_patch_set_list(application: Application, mocker: MockerFixture) -> None:
    """
    must list available patches for the command
    """
    get_mock = mocker.patch("ahriman.core.database.sqlite.SQLite.patches_list", return_value={"ahriman": "patch"})
    print_mock = mocker.patch("ahriman.core.formatters.printer.Printer.print")
    check_mock = mocker.patch("ahriman.application.handlers.handler.Handler.check_if_empty")

    Patch.patch_set_list(application, "ahriman", False)
    get_mock.assert_called_once_with("ahriman")
    print_mock.assert_called_once_with(verbose=True)
    check_mock.assert_called_once_with(False, False)


def test_patch_set_list_empty_exception(application: Application, mocker: MockerFixture) -> None:
    """
    must raise ExitCode exception on empty patch list
    """
    mocker.patch("ahriman.core.database.sqlite.SQLite.patches_list", return_value={})
    check_mock = mocker.patch("ahriman.application.handlers.handler.Handler.check_if_empty")

    Patch.patch_set_list(application, "ahriman", True)
    check_mock.assert_called_once_with(True, True)


def test_patch_set_create(application: Application, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must create patch set for the package
    """
    mocker.patch("pathlib.Path.mkdir")
    mocker.patch("ahriman.models.package.Package.load", return_value=package_ahriman)
    mocker.patch("ahriman.core.build_tools.sources.Sources.patch_create", return_value="patch")
    create_mock = mocker.patch("ahriman.core.database.sqlite.SQLite.patches_insert")

    Patch.patch_set_create(application, "path", ["*.patch"])
    create_mock.assert_called_once_with(package_ahriman.base, "patch")


def test_patch_set_remove(application: Application, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must remove patch set for the package
    """
    remove_mock = mocker.patch("ahriman.core.database.sqlite.SQLite.patches_remove")
    Patch.patch_set_remove(application, package_ahriman.base)
    remove_mock.assert_called_once_with(package_ahriman.base)
