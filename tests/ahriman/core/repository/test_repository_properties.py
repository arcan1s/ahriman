from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.exceptions import UnsafeRunError
from ahriman.core.repository.repository_properties import RepositoryProperties
from ahriman.core.status.web_client import WebClient


def test_create_tree_on_load(configuration: Configuration, database: SQLite, mocker: MockerFixture) -> None:
    """
    must create tree on load
    """
    mocker.patch("ahriman.core.repository.repository_properties.check_user")
    tree_create_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    RepositoryProperties("x86_64", configuration, database, report=False, unsafe=False)

    tree_create_mock.assert_called_once_with()


def test_create_tree_on_load_unsafe(configuration: Configuration, database: SQLite, mocker: MockerFixture) -> None:
    """
    must not create tree on load in case if user differs from the root owner
    """
    mocker.patch("ahriman.core.repository.repository_properties.check_user", side_effect=UnsafeRunError(0, 1))
    tree_create_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    RepositoryProperties("x86_64", configuration, database, report=False, unsafe=False)

    tree_create_mock.assert_not_called()


def test_create_dummy_report_client(configuration: Configuration, database: SQLite, mocker: MockerFixture) -> None:
    """
    must create dummy report client if report is disabled
    """
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    load_mock = mocker.patch("ahriman.core.status.client.Client.load")
    properties = RepositoryProperties("x86_64", configuration, database, report=False, unsafe=False)

    load_mock.assert_not_called()
    assert not isinstance(properties.reporter, WebClient)


def test_create_full_report_client(configuration: Configuration, database: SQLite, mocker: MockerFixture) -> None:
    """
    must create load report client if report is enabled
    """
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    load_mock = mocker.patch("ahriman.core.status.client.Client.load")
    RepositoryProperties("x86_64", configuration, database, report=True, unsafe=True)

    load_mock.assert_called_once_with(configuration)
