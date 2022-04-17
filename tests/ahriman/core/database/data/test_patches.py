import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from sqlite3 import Connection

from ahriman.core.database.data import migrate_patches
from ahriman.models.package import Package
from ahriman.models.repository_paths import RepositoryPaths


def test_migrate_patches(connection: Connection, repository_paths: RepositoryPaths,
                         package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must perform migration for patches
    """
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("pathlib.Path.is_file", return_value=True)
    iterdir_mock = mocker.patch("pathlib.Path.iterdir", return_value=[Path(package_ahriman.base)])
    read_mock = mocker.patch("pathlib.Path.read_text", return_value="patch")

    migrate_patches(connection, repository_paths)
    iterdir_mock.assert_called_once_with()
    read_mock.assert_called_once_with(encoding="utf8")
    connection.execute.assert_called_once_with(pytest.helpers.anyvar(str, strict=True), pytest.helpers.anyvar(int))


def test_migrate_patches_skip(connection: Connection, repository_paths: RepositoryPaths,
                              mocker: MockerFixture) -> None:
    """
    must skip patches migration in case if no root found
    """
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    iterdir_mock = mocker.patch("pathlib.Path.iterdir")

    migrate_patches(connection, repository_paths)
    iterdir_mock.assert_not_called()


def test_migrate_patches_no_patch(connection: Connection, repository_paths: RepositoryPaths,
                                  package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must skip package if no match found
    """
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("pathlib.Path.is_file", return_value=False)
    iterdir_mock = mocker.patch("pathlib.Path.iterdir", return_value=[Path(package_ahriman.base)])
    read_mock = mocker.patch("pathlib.Path.read_text")

    migrate_patches(connection, repository_paths)
    iterdir_mock.assert_called_once_with()
    read_mock.assert_not_called()
