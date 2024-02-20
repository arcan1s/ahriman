import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.core.build_tools.task import Task
from ahriman.core.database import SQLite


def test_build(task_ahriman: Task, mocker: MockerFixture) -> None:
    """
    must build package
    """
    local = Path("local")
    check_output_mock = mocker.patch("ahriman.core.build_tools.task.check_output")

    task_ahriman.build(local)
    check_output_mock.assert_has_calls([
        MockCall(
            "extra-x86_64-build", "-r", str(task_ahriman.paths.chroot), "--", "--", "--skippgpcheck",
            exception=pytest.helpers.anyvar(int),
            cwd=local,
            logger=task_ahriman.logger,
            user=task_ahriman.uid,
            environment={},
        ),
        MockCall(
            "makepkg", "--packagelist",
            exception=pytest.helpers.anyvar(int),
            cwd=local,
            logger=task_ahriman.logger,
            environment={},
        ),
    ])


def test_build_environment(task_ahriman: Task, mocker: MockerFixture) -> None:
    """
    must build package with environment variables set
    """
    local = Path("local")
    check_output_mock = mocker.patch("ahriman.core.build_tools.task.check_output")
    environment = {"variable": "value"}

    task_ahriman.build(local, **environment, empty=None)
    check_output_mock.assert_has_calls([
        MockCall(
            "extra-x86_64-build", "-r", str(task_ahriman.paths.chroot), "--", "--", "--skippgpcheck",
            exception=pytest.helpers.anyvar(int),
            cwd=local,
            logger=task_ahriman.logger,
            user=task_ahriman.uid,
            environment=environment,
        ),
        MockCall(
            "makepkg", "--packagelist",
            exception=pytest.helpers.anyvar(int),
            cwd=local,
            logger=task_ahriman.logger,
            environment=environment,
        ),
    ])


def test_build_no_debug(task_ahriman: Task, mocker: MockerFixture) -> None:
    """
    must filter debug packages from result
    """
    local = Path("local")
    check_output_mock = mocker.patch("ahriman.core.build_tools.task.check_output")
    task_ahriman.include_debug_packages = False

    task_ahriman.build(local)
    check_output_mock.assert_has_calls([
        MockCall(
            "extra-x86_64-build", "-r", str(task_ahriman.paths.chroot), "--", "--", "--skippgpcheck",
            exception=pytest.helpers.anyvar(int),
            cwd=local,
            logger=task_ahriman.logger,
            user=task_ahriman.uid,
            environment={},
        ),
        MockCall(
            "makepkg", "--packagelist", "OPTIONS=(!debug)",
            exception=pytest.helpers.anyvar(int),
            cwd=local,
            logger=task_ahriman.logger,
            environment={},
        ),
    ])


def test_init(task_ahriman: Task, database: SQLite, mocker: MockerFixture) -> None:
    """
    must copy tree instead of fetch
    """
    mocker.patch("ahriman.models.package.Package.from_build", return_value=task_ahriman.package)
    load_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.load", return_value="sha")

    assert task_ahriman.init(Path("ahriman"), database, None) == "sha"
    load_mock.assert_called_once_with(Path("ahriman"), task_ahriman.package, [], task_ahriman.paths)


def test_init_bump_pkgrel(task_ahriman: Task, database: SQLite, mocker: MockerFixture) -> None:
    """
    must bump pkgrel if it is same as provided
    """
    mocker.patch("ahriman.models.package.Package.from_build", return_value=task_ahriman.package)
    mocker.patch("ahriman.core.build_tools.sources.Sources.load", return_value="sha")
    write_mock = mocker.patch("ahriman.models.pkgbuild_patch.PkgbuildPatch.write")

    local = Path("ahriman")
    assert task_ahriman.init(local, database, task_ahriman.package.version) == "sha"
    write_mock.assert_called_once_with(local / "PKGBUILD")


def test_init_bump_pkgrel_skip(task_ahriman: Task, database: SQLite, mocker: MockerFixture) -> None:
    """
    must keep pkgrel if version is different from provided
    """
    mocker.patch("ahriman.models.package.Package.from_build", return_value=task_ahriman.package)
    mocker.patch("ahriman.core.build_tools.sources.Sources.load", return_value="sha")
    write_mock = mocker.patch("ahriman.models.pkgbuild_patch.PkgbuildPatch.write")

    assert task_ahriman.init(Path("ahriman"), database, f"2:{task_ahriman.package.version}") == "sha"
    write_mock.assert_not_called()
