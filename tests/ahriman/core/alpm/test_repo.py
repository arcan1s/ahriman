import os
import pytest

from pytest_mock import MockerFixture
from unittest import mock

from ahriman.core.alpm.repo import Repo


def test_repo_path(repo: Repo) -> None:
    """
    name must be something like archive name
    """
    assert repo.repo_path.endswith("db.tar.gz")


def test_repo_add(repo: Repo, mocker: MockerFixture) -> None:
    """
    must call repo-add on package addition
    """
    check_output_mock = mocker.patch("ahriman.core.alpm.repo.Repo._check_output")

    repo.add("path")
    Repo._check_output.assert_called_once()
    assert check_output_mock.call_args[0][0] == "repo-add"


def test_repo_remove(repo: Repo, mocker: MockerFixture) -> None:
    """
    must call repo-remove on package addition
    """
    mocker.patch("os.listdir", return_value=[])
    check_output_mock = mocker.patch("ahriman.core.alpm.repo.Repo._check_output")

    repo.remove("package", "package.pkg.tar.xz")
    Repo._check_output.assert_called_once()
    assert check_output_mock.call_args[0][0] == "repo-remove"


def test_repo_remove_fail_no_file(repo: Repo, mocker: MockerFixture) -> None:
    """
    must fail on missing file
    """
    mocker.patch("os.listdir", return_value=["package.pkg.tar.xz"])
    mocker.patch("os.remove", side_effect=FileNotFoundError())

    with pytest.raises(FileNotFoundError):
        repo.remove("package", "package.pkg.tar.xz")


def test_repo_remove_remove_requested(repo: Repo, mocker: MockerFixture) -> None:
    """
    must remove only requested files
    """
    packages = ["package.pkg.tar.xz", "package.pkg.tar.xz.sig"]
    all_packages = packages + ["valid-package.pkg.tar.xz.sig", "package-valid.pkg.tar.xz.sig"]

    mocker.patch("os.listdir", return_value=all_packages)
    remove_mock = mocker.patch("os.remove")
    mocker.patch("ahriman.core.alpm.repo.Repo._check_output")

    repo.remove("package", "package.pkg.tar.xz")
    removed = [call.call_list()[0][0][0] for call in remove_mock.call_args_list]
    to_be_removed = [os.path.join(repo.paths.repository, package) for package in packages]
    assert set(removed) == set(to_be_removed)
