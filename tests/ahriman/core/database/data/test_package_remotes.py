import pytest

from pytest_mock import MockerFixture
from sqlite3 import Connection

from ahriman.core.database.data import migrate_package_remotes
from ahriman.models.package import Package
from ahriman.models.repository_paths import RepositoryPaths


def test_migrate_package_remotes(package_ahriman: Package, connection: Connection, repository_paths: RepositoryPaths,
                                 mocker: MockerFixture) -> None:
    """
    must put package remotes to database
    """
    mocker.patch(
        "ahriman.core.database.operations.package_operations.PackageOperations._packages_get_select_package_bases",
        return_value={package_ahriman.base: package_ahriman})
    mocker.patch("pathlib.Path.exists", return_value=False)

    migrate_package_remotes(connection, repository_paths)
    connection.execute.assert_called_once_with(pytest.helpers.anyvar(str, strict=True), pytest.helpers.anyvar(int))


def test_migrate_package_remotes_has_local(package_ahriman: Package, connection: Connection,
                                           repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must skip processing for packages which have local cache
    """
    mocker.patch(
        "ahriman.core.database.operations.package_operations.PackageOperations._packages_get_select_package_bases",
        return_value={package_ahriman.base: package_ahriman})
    mocker.patch("pathlib.Path.exists", return_value=True)

    migrate_package_remotes(connection, repository_paths)
    connection.execute.assert_not_called()


def test_migrate_package_remotes_vcs(package_ahriman: Package, connection: Connection,
                                     repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must process VCS packages with local cache
    """
    mocker.patch(
        "ahriman.core.database.operations.package_operations.PackageOperations._packages_get_select_package_bases",
        return_value={package_ahriman.base: package_ahriman})
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch.object(Package, "is_vcs", True)

    migrate_package_remotes(connection, repository_paths)
    connection.execute.assert_called_once_with(pytest.helpers.anyvar(str, strict=True), pytest.helpers.anyvar(int))


def test_migrate_package_remotes_no_remotes(package_ahriman: Package, connection: Connection,
                                            repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must skip processing in case if no remotes generated (should never happen)
    """
    mocker.patch(
        "ahriman.core.database.operations.package_operations.PackageOperations._packages_get_select_package_bases",
        return_value={package_ahriman.base: package_ahriman})
    mocker.patch("pathlib.Path.exists", return_value=False)
    mocker.patch("ahriman.models.remote_source.RemoteSource.from_source", return_value=None)

    migrate_package_remotes(connection, repository_paths)
    connection.execute.assert_not_called()
