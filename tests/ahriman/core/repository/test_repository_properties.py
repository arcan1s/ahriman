from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.exceptions import UnsafeRunError
from ahriman.core.repository.repository_properties import RepositoryProperties


def test_create_tree_on_load(configuration: Configuration, database: SQLite, mocker: MockerFixture) -> None:
    """
    must create tree on load
    """
    mocker.patch("ahriman.core.repository.repository_properties.check_user")
    tree_create_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    RepositoryProperties("x86_64", configuration, database, report=False, unsafe=False, refresh_pacman_database=0)

    tree_create_mock.assert_called_once_with()


def test_create_tree_on_load_unsafe(configuration: Configuration, database: SQLite, mocker: MockerFixture) -> None:
    """
    must not create tree on load in case if user differs from the root owner
    """
    mocker.patch("ahriman.core.repository.repository_properties.check_user", side_effect=UnsafeRunError(0, 1))
    tree_create_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    RepositoryProperties("x86_64", configuration, database, report=False, unsafe=False, refresh_pacman_database=0)

    tree_create_mock.assert_not_called()
