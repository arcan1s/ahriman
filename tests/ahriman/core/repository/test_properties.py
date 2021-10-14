from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import UnsafeRun
from ahriman.core.repository.properties import Properties
from ahriman.core.status.web_client import WebClient


def test_create_tree_on_load(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must create tree on load
    """
    mocker.patch("ahriman.core.repository.properties.check_user")
    tree_create_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    Properties("x86_64", configuration, True)

    tree_create_mock.assert_called_once()


def test_create_tree_on_load_unsafe(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must not create tree on load in case if user differs from the root owner
    """
    mocker.patch("ahriman.core.repository.properties.check_user", side_effect=UnsafeRun(0, 1))
    tree_create_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    Properties("x86_64", configuration, True)

    tree_create_mock.assert_not_called()


def test_create_dummy_report_client(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must create dummy report client if report is disabled
    """
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    load_mock = mocker.patch("ahriman.core.status.client.Client.load")
    properties = Properties("x86_64", configuration, True)

    load_mock.assert_not_called()
    assert not isinstance(properties.reporter, WebClient)


def test_create_full_report_client(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must create load report client if report is enabled
    """
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    load_mock = mocker.patch("ahriman.core.status.client.Client.load")
    Properties("x86_64", configuration, False)

    load_mock.assert_called_once()
