import argparse
import pytest
import sys

from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.application.application import Application
from ahriman.application.handlers import Patch
from ahriman.core.configuration import Configuration
from ahriman.core.repository import Repository
from ahriman.models.action import Action
from ahriman.models.package import Package
from ahriman.models.pkgbuild_patch import PkgbuildPatch


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
        args(argparse.Namespace): command line arguments fixture

    Returns:
        argparse.Namespace: generated arguments for these test cases
    """
    args.package = "ahriman"
    args.exit_code = False
    args.remove = False
    args.track = ["*.diff", "*.patch"]
    args.variable = None
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, repository: Repository,
             mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    args.action = Action.Update
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    patch_mock = mocker.patch("ahriman.application.handlers.Patch.patch_create_from_diff",
                              return_value=(args.package, PkgbuildPatch(None, "patch")))
    application_mock = mocker.patch("ahriman.application.handlers.Patch.patch_set_create")

    _, repository_id = configuration.check_loaded()
    Patch.run(args, repository_id, configuration, report=False)
    patch_mock.assert_called_once_with(args.package, repository_id.architecture, args.track)
    application_mock.assert_called_once_with(pytest.helpers.anyvar(int), args.package, PkgbuildPatch(None, "patch"))


def test_run_function(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                      mocker: MockerFixture) -> None:
    """
    must run command with patch function flag
    """
    args = _default_args(args)
    args.action = Action.Update
    args.patch = "patch"
    args.variable = "version"
    patch = PkgbuildPatch(args.variable, args.patch)
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    patch_mock = mocker.patch("ahriman.application.handlers.Patch.patch_create_from_function", return_value=patch)
    application_mock = mocker.patch("ahriman.application.handlers.Patch.patch_set_create")

    _, repository_id = configuration.check_loaded()
    Patch.run(args, repository_id, configuration, report=False)
    patch_mock.assert_called_once_with(args.variable, args.patch)
    application_mock.assert_called_once_with(pytest.helpers.anyvar(int), args.package, patch)


def test_run_list(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                  mocker: MockerFixture) -> None:
    """
    must run command with list flag
    """
    args = _default_args(args)
    args.action = Action.List
    args.variable = ["version"]
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    application_mock = mocker.patch("ahriman.application.handlers.Patch.patch_set_list")

    _, repository_id = configuration.check_loaded()
    Patch.run(args, repository_id, configuration, report=False)
    application_mock.assert_called_once_with(pytest.helpers.anyvar(int), args.package, ["version"], False)


def test_run_remove(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                    mocker: MockerFixture) -> None:
    """
    must run command with remove flag
    """
    args = _default_args(args)
    args.action = Action.Remove
    args.variable = ["version"]
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    application_mock = mocker.patch("ahriman.application.handlers.Patch.patch_set_remove")

    _, repository_id = configuration.check_loaded()
    Patch.run(args, repository_id, configuration, report=False)
    application_mock.assert_called_once_with(pytest.helpers.anyvar(int), args.package, ["version"])


def test_patch_create_from_diff(package_ahriman: Package, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must create patch from directory tree diff
    """
    patch = PkgbuildPatch(None, "patch")
    path = Path("local")
    mocker.patch("pathlib.Path.mkdir")
    package_mock = mocker.patch("ahriman.models.package.Package.from_build", return_value=package_ahriman)
    sources_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.patch_create", return_value=patch.value)

    _, repository_id = configuration.check_loaded()
    assert Patch.patch_create_from_diff(path, repository_id.architecture, ["*.diff"]) == (package_ahriman.base, patch)
    package_mock.assert_called_once_with(path, repository_id.architecture, None)
    sources_mock.assert_called_once_with(path, "*.diff")


def test_patch_create_from_function(mocker: MockerFixture) -> None:
    """
    must create function patch from file
    """
    path = Path("local")
    patch = PkgbuildPatch("version", "patch")
    read_mock = mocker.patch("pathlib.Path.read_text", return_value=patch.value)

    assert Patch.patch_create_from_function(patch.key, path) == patch
    read_mock.assert_called_once_with(encoding="utf8")


def test_patch_create_from_function_stdin(mocker: MockerFixture) -> None:
    """
    must create function patch from stdin
    """
    patch = PkgbuildPatch("version", "This is a patch")
    mocker.patch.object(sys, "stdin", patch.value.splitlines())
    assert Patch.patch_create_from_function(patch.key, None) == patch


def test_patch_create_from_function_strip(mocker: MockerFixture) -> None:
    """
    must remove spaces at the beginning and at the end of the line
    """
    patch = PkgbuildPatch("version", "This is a patch")
    mocker.patch.object(sys, "stdin", ["\n"] + patch.value.splitlines() + ["\n"])
    assert Patch.patch_create_from_function(patch.key, None) == patch


def test_patch_set_list(application: Application, mocker: MockerFixture) -> None:
    """
    must list available patches for the command
    """
    get_mock = mocker.patch("ahriman.core.database.SQLite.patches_list",
                            return_value={"ahriman": PkgbuildPatch(None, "patch")})
    print_mock = mocker.patch("ahriman.core.formatters.Printer.print")
    check_mock = mocker.patch("ahriman.application.handlers.Handler.check_if_empty")

    Patch.patch_set_list(application, "ahriman", ["version"], False)
    get_mock.assert_called_once_with("ahriman", ["version"])
    print_mock.assert_called_once_with(verbose=True, separator=" = ")
    check_mock.assert_called_once_with(False, False)


def test_patch_set_list_empty_exception(application: Application, mocker: MockerFixture) -> None:
    """
    must raise ExitCode exception on empty patch list
    """
    mocker.patch("ahriman.core.database.SQLite.patches_list", return_value={})
    check_mock = mocker.patch("ahriman.application.handlers.Handler.check_if_empty")

    Patch.patch_set_list(application, "ahriman", [], True)
    check_mock.assert_called_once_with(True, True)


def test_patch_set_create(application: Application, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must create patch set for the package
    """
    create_mock = mocker.patch("ahriman.core.database.SQLite.patches_insert")
    Patch.patch_set_create(application, package_ahriman.base, PkgbuildPatch("version", package_ahriman.version))
    create_mock.assert_called_once_with(package_ahriman.base, PkgbuildPatch("version", package_ahriman.version))


def test_patch_set_remove(application: Application, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must remove patch set for the package
    """
    remove_mock = mocker.patch("ahriman.core.database.SQLite.patches_remove")
    Patch.patch_set_remove(application, package_ahriman.base, ["version"])
    remove_mock.assert_called_once_with(package_ahriman.base, ["version"])


def test_disallow_multi_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not Patch.ALLOW_MULTI_ARCHITECTURE_RUN
