from pytest_mock import MockerFixture

from ahriman.core.repository.repository_properties import RepositoryProperties
from ahriman.models.packagers import Packagers
from ahriman.models.user import User
from ahriman.models.user_access import UserAccess


def test_packager(repository: RepositoryProperties, mocker: MockerFixture) -> None:
    """
    must extract packager
    """
    database_mock = mocker.patch("ahriman.core.database.SQLite.user_get")
    assert repository.packager(Packagers("username", {}), "base")
    database_mock.assert_called_once_with("username")


def test_packager_empty(repository: RepositoryProperties, mocker: MockerFixture) -> None:
    """
    must return empty user if username was not set
    """
    database_mock = mocker.patch("ahriman.core.database.SQLite.user_get")
    user = User(username="", password="", access=UserAccess.Read, packager_id=None, key=None)
    assert repository.packager(Packagers(), "base") == user
    database_mock.assert_not_called()


def test_packager_empty_result(repository: RepositoryProperties, mocker: MockerFixture) -> None:
    """
    must return empty user if it wasn't found in database
    """
    database_mock = mocker.patch("ahriman.core.database.SQLite.user_get", return_value=None)
    user = User(username="username", password="", access=UserAccess.Read, packager_id=None, key=None)
    assert repository.packager(Packagers(user.username), "base") == user
    database_mock.assert_called_once_with(user.username)
