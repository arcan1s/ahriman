from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.repository.properties import Properties
from ahriman.core.status.web_client import WebClient


def test_create_tree_on_load(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must create tree on load
    """
    create_tree_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.create_tree")
    Properties("x86_64", configuration, True)

    create_tree_mock.assert_called_once()


def test_create_dummy_report_client(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must create dummy report client if report is disabled
    """
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.create_tree")
    load_mock = mocker.patch("ahriman.core.status.client.Client.load")
    properties = Properties("x86_64", configuration, True)

    load_mock.assert_not_called()
    assert not isinstance(properties.reporter, WebClient)


def test_create_full_report_client(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must create load report client if report is enabled
    """
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.create_tree")
    load_mock = mocker.patch("ahriman.core.status.client.Client.load")
    Properties("x86_64", configuration, False)

    load_mock.assert_called_once()
