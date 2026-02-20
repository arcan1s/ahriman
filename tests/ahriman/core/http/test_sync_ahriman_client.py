import pytest
import requests

from pytest_mock import MockerFixture

from ahriman.core.http import SyncAhrimanClient
from ahriman.models.user import User


def test_adapters(ahriman_client: SyncAhrimanClient) -> None:
    """
    must return native adapters
    """
    assert "http+unix://" not in ahriman_client.adapters()


def test_adapters_unix_socket(ahriman_client: SyncAhrimanClient) -> None:
    """
    must register unix socket adapter
    """
    ahriman_client.address = "http+unix://path"
    assert "http+unix://" in ahriman_client.adapters()


def test_login_url(ahriman_client: SyncAhrimanClient) -> None:
    """
    must generate login url correctly
    """
    assert ahriman_client._login_url().startswith(ahriman_client.address)
    assert ahriman_client._login_url().endswith("/api/v1/login")


def test_on_session_creation(ahriman_client: SyncAhrimanClient, user: User, mocker: MockerFixture) -> None:
    """
    must log in user on start
    """
    ahriman_client.auth = (user.username, user.password)
    requests_mock = mocker.patch("ahriman.core.http.SyncAhrimanClient.make_request")
    payload = {
        "username": user.username,
        "password": user.password
    }
    session = requests.Session()

    ahriman_client.on_session_creation(session)
    requests_mock.assert_called_once_with("POST", pytest.helpers.anyvar(str, True), json=payload, session=session)


def test_on_session_creation_failed(ahriman_client: SyncAhrimanClient, user: User, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during session start
    """
    ahriman_client.user = user
    mocker.patch("requests.Session.request", side_effect=Exception)
    ahriman_client.on_session_creation(requests.Session())


def test_start_failed_http_error(ahriman_client: SyncAhrimanClient, user: User, mocker: MockerFixture) -> None:
    """
    must suppress HTTP exception happened during session start
    """
    ahriman_client.user = user
    mocker.patch("requests.Session.request", side_effect=requests.HTTPError)
    ahriman_client.on_session_creation(requests.Session())


def test_start_skip(ahriman_client: SyncAhrimanClient, mocker: MockerFixture) -> None:
    """
    must skip login if no user set
    """
    requests_mock = mocker.patch("requests.Session.request")
    ahriman_client.on_session_creation(requests.Session())
    requests_mock.assert_not_called()
