import pytest
import requests
import requests_unixsocket

from pytest_mock import MockerFixture

from ahriman.core.http import SyncAhrimanClient
from ahriman.models.user import User


def test_session(ahriman_client: SyncAhrimanClient, mocker: MockerFixture) -> None:
    """
    must create normal requests session
    """
    login_mock = mocker.patch("ahriman.core.http.SyncAhrimanClient._login")

    assert isinstance(ahriman_client.session, requests.Session)
    assert not isinstance(ahriman_client.session, requests_unixsocket.Session)
    login_mock.assert_called_once_with(pytest.helpers.anyvar(int))


def test_session_unix_socket(ahriman_client: SyncAhrimanClient, mocker: MockerFixture) -> None:
    """
    must create unix socket session
    """
    login_mock = mocker.patch("ahriman.core.http.SyncAhrimanClient._login")
    ahriman_client.address = "http+unix://path"

    assert isinstance(ahriman_client.session, requests_unixsocket.Session)
    login_mock.assert_not_called()


def test_login(ahriman_client: SyncAhrimanClient, user: User, mocker: MockerFixture) -> None:
    """
    must login user
    """
    ahriman_client.auth = (user.username, user.password)
    requests_mock = mocker.patch("ahriman.core.http.SyncAhrimanClient.make_request")
    payload = {
        "username": user.username,
        "password": user.password
    }
    session = requests.Session()

    ahriman_client._login(session)
    requests_mock.assert_called_once_with("POST", pytest.helpers.anyvar(str, True), json=payload, session=session)


def test_login_failed(ahriman_client: SyncAhrimanClient, user: User, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during login
    """
    ahriman_client.user = user
    mocker.patch("requests.Session.request", side_effect=Exception)
    ahriman_client._login(requests.Session())


def test_login_failed_http_error(ahriman_client: SyncAhrimanClient, user: User, mocker: MockerFixture) -> None:
    """
    must suppress HTTP exception happened during login
    """
    ahriman_client.user = user
    mocker.patch("requests.Session.request", side_effect=requests.HTTPError)
    ahriman_client._login(requests.Session())


def test_login_skip(ahriman_client: SyncAhrimanClient, mocker: MockerFixture) -> None:
    """
    must skip login if no user set
    """
    requests_mock = mocker.patch("requests.Session.request")
    ahriman_client._login(requests.Session())
    requests_mock.assert_not_called()


def test_login_url(ahriman_client: SyncAhrimanClient) -> None:
    """
    must generate login url correctly
    """
    assert ahriman_client._login_url().startswith(ahriman_client.address)
    assert ahriman_client._login_url().endswith("/api/v1/login")
