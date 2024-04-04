import pytest

from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.core.alpm.repo import Repo


def test_repo_path(repo: Repo) -> None:
    """
    name must be something like archive name
    """
    assert repo.repo_path.name.endswith("db.tar.gz")


def test_repo_add(repo: Repo, mocker: MockerFixture) -> None:
    """
    must call repo-add on package addition
    """
    check_output_mock = mocker.patch("ahriman.core.alpm.repo.check_output")

    repo.add(Path("path"))
    check_output_mock.assert_called_once()  # it will be checked later
    assert check_output_mock.call_args[0][0] == "repo-add"


def test_repo_init(repo: Repo, mocker: MockerFixture) -> None:
    """
    must create empty database files
    """
    mocker.patch("pathlib.Path.exists", return_value=False)
    touch_mock = mocker.patch("pathlib.Path.touch")
    symlink_mock = mocker.patch("pathlib.Path.symlink_to")

    repo.init()
    touch_mock.assert_called_once_with(exist_ok=True)
    symlink_mock.assert_called_once_with(repo.repo_path)


def test_repo_init_skip(repo: Repo, mocker: MockerFixture) -> None:
    """
    must do not create files if database already exists
    """
    mocker.patch("pathlib.Path.exists", return_value=True)
    touch_mock = mocker.patch("pathlib.Path.touch")
    symlink_mock = mocker.patch("pathlib.Path.symlink_to")

    repo.init()
    touch_mock.assert_not_called()
    symlink_mock.assert_not_called()


def test_repo_remove(repo: Repo, mocker: MockerFixture) -> None:
    """
    must call repo-remove on package addition
    """
    mocker.patch("pathlib.Path.glob", return_value=[])
    check_output_mock = mocker.patch("ahriman.core.alpm.repo.check_output")

    repo.remove("package", Path("package.pkg.tar.xz"))
    check_output_mock.assert_called_once()  # it will be checked later
    assert check_output_mock.call_args[0][0] == "repo-remove"


def test_repo_remove_fail_no_file(repo: Repo, mocker: MockerFixture) -> None:
    """
    must fail on missing file
    """
    mocker.patch("pathlib.Path.glob", return_value=[Path("package.pkg.tar.xz")])
    mocker.patch("pathlib.Path.unlink", side_effect=FileNotFoundError())

    with pytest.raises(FileNotFoundError):
        repo.remove("package", Path("package.pkg.tar.xz"))
