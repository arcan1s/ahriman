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
    check_output_mock = mocker.patch("ahriman.core.alpm.repo.Repo._check_output")

    repo.add(Path("path"))
    check_output_mock.assert_called_once()  # it will be checked later
    assert check_output_mock.call_args[0][0] == "repo-add"


def test_repo_init(repo: Repo, mocker: MockerFixture) -> None:
    """
    must call repo-add with empty package list on repo initializing
    """
    check_output_mock = mocker.patch("ahriman.core.alpm.repo.Repo._check_output")

    repo.init()
    check_output_mock.assert_called_once()  # it will be checked later
    assert check_output_mock.call_args[0][0] == "repo-add"


def test_repo_remove(repo: Repo, mocker: MockerFixture) -> None:
    """
    must call repo-remove on package addition
    """
    mocker.patch("pathlib.Path.glob", return_value=[])
    check_output_mock = mocker.patch("ahriman.core.alpm.repo.Repo._check_output")

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
