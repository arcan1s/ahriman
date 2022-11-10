import pytest

from pytest_mock import MockerFixture
from sqlite3 import Connection
from unittest.mock import call as MockCall

from ahriman.core.database.data import migrate_package_statuses
from ahriman.models.package import Package
from ahriman.models.repository_paths import RepositoryPaths


def test_migrate_package_statuses(connection: Connection, package_ahriman: Package, repository_paths: RepositoryPaths,
                                  mocker: MockerFixture) -> None:
    """
    must migrate packages to database
    """
    response = {"packages": [pytest.helpers.get_package_status_extended(package_ahriman)]}

    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("pathlib.Path.open")
    mocker.patch("json.load", return_value=response)

    migrate_package_statuses(connection, repository_paths)
    connection.execute.assert_has_calls([
        MockCall(pytest.helpers.anyvar(str, strict=True), pytest.helpers.anyvar(int)),
        MockCall(pytest.helpers.anyvar(str, strict=True), pytest.helpers.anyvar(int)),
    ])
    connection.executemany.assert_has_calls([
        MockCall(pytest.helpers.anyvar(str, strict=True), pytest.helpers.anyvar(int)),
    ])


def test_migrate_package_statuses_skip(connection: Connection, repository_paths: RepositoryPaths,
                                       mocker: MockerFixture) -> None:
    """
    must skip packages migration if no cache file found
    """
    mocker.patch("pathlib.Path.is_file", return_value=False)
    migrate_package_statuses(connection, repository_paths)
