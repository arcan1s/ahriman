from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.exceptions import UnsafeRunError
from ahriman.core.repository.repository_properties import RepositoryProperties
from ahriman.models.packagers import Packagers
from ahriman.models.pacman_synchronization import PacmanSynchronization
from ahriman.models.user import User
from ahriman.models.user_access import UserAccess


def test_create_tree_on_load(configuration: Configuration, database: SQLite, mocker: MockerFixture) -> None:
    """
    must create tree on load
    """
    mocker.patch("ahriman.core.repository.repository_properties.check_user")
    tree_create_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    RepositoryProperties("x86_64", configuration, database, report=False, unsafe=False,
                         refresh_pacman_database=PacmanSynchronization.Disabled)

    tree_create_mock.assert_called_once_with()


def test_create_tree_on_load_unsafe(configuration: Configuration, database: SQLite, mocker: MockerFixture) -> None:
    """
    must not create tree on load in case if user differs from the root owner
    """
    mocker.patch("ahriman.core.repository.repository_properties.check_user", side_effect=UnsafeRunError(0, 1))
    tree_create_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    RepositoryProperties("x86_64", configuration, database, report=False, unsafe=False,
                         refresh_pacman_database=PacmanSynchronization.Disabled)

    tree_create_mock.assert_not_called()


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
