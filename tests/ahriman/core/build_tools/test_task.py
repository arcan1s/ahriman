from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.core.build_tools.task import Task
from ahriman.core.database import SQLite


def test_build(task_ahriman: Task, mocker: MockerFixture) -> None:
    """
    must build package
    """
    check_output_mock = mocker.patch("ahriman.core.build_tools.task.Task._check_output")
    task_ahriman.build(Path("ahriman"))
    check_output_mock.assert_called()


def test_init(task_ahriman: Task, database: SQLite, mocker: MockerFixture) -> None:
    """
    must copy tree instead of fetch
    """
    mocker.patch("ahriman.models.package.Package.from_build", return_value=task_ahriman.package)
    load_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.load")
    task_ahriman.init(Path("ahriman"), database, None)
    load_mock.assert_called_once_with(Path("ahriman"), task_ahriman.package, [], task_ahriman.paths)


def test_init_bump_pkgrel(task_ahriman: Task, database: SQLite, mocker: MockerFixture) -> None:
    """
    must bump pkgrel if it is same as provided
    """
    mocker.patch("ahriman.models.package.Package.from_build", return_value=task_ahriman.package)
    mocker.patch("ahriman.core.build_tools.sources.Sources.load")
    write_mock = mocker.patch("ahriman.models.pkgbuild_patch.PkgbuildPatch.write")

    local = Path("ahriman")
    task_ahriman.init(local, database, task_ahriman.package.version)
    write_mock.assert_called_once_with(local / "PKGBUILD")


def test_init_bump_pkgrel_skip(task_ahriman: Task, database: SQLite, mocker: MockerFixture) -> None:
    """
    must keep pkgrel if version is different from provided
    """
    mocker.patch("ahriman.models.package.Package.from_build", return_value=task_ahriman.package)
    mocker.patch("ahriman.core.build_tools.sources.Sources.load")
    write_mock = mocker.patch("ahriman.models.pkgbuild_patch.PkgbuildPatch.write")

    task_ahriman.init(Path("ahriman"), database, f"2:{task_ahriman.package.version}")
    write_mock.assert_not_called()
