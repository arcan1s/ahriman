import pytest
import requests

from pytest_mock import MockerFixture
from unittest.mock import MagicMock, call as MockCall

from ahriman.core.configuration import Configuration
from ahriman.core.http import SyncHttpClient


def test_init() -> None:
    """
    must init from empty parameters
    """
    assert SyncHttpClient()


def test_init_auth(configuration: Configuration) -> None:
    """
    must init with auth
    """
    configuration.set_option("web", "username", "username")
    configuration.set_option("web", "password", "password")

    assert SyncHttpClient(configuration, "web").auth == ("username", "password")
    assert SyncHttpClient(configuration=configuration).auth is None


def test_init_auth_empty() -> None:
    """
    must init with empty auth
    """
    assert SyncHttpClient().auth is None


def test_session() -> None:
    """
    must generate valid session
    """
    session = SyncHttpClient().session
    assert "User-Agent" in session.headers


def test_exception_response_text() -> None:
    """
    must parse HTTP response to string
    """
    response_mock = MagicMock()
    response_mock.text = "hello"
    exception = requests.exceptions.HTTPError(response=response_mock)

    assert SyncHttpClient.exception_response_text(exception) == "hello"


def test_exception_response_text_empty() -> None:
    """
    must parse HTTP exception with empty response to empty string
    """
    exception = requests.exceptions.HTTPError(response=None)
    assert SyncHttpClient.exception_response_text(exception) == ""


def test_make_request(mocker: MockerFixture) -> None:
    """
    must make HTTP request
    """
    request_mock = mocker.patch("requests.Session.request")
    client = SyncHttpClient()

    assert client.make_request("GET", "url1") is not None
    assert client.make_request("GET", "url2", params=[("param", "value")]) is not None

    assert client.make_request("POST", "url3") is not None
    assert client.make_request("POST", "url4", json={"param": "value"}) is not None
    assert client.make_request("POST", "url5", data={"param": "value"}) is not None
    # we don't want to put full descriptor here
    assert client.make_request("POST", "url6", files={"file": "tuple"}) is not None

    assert client.make_request("DELETE", "url7") is not None

    assert client.make_request("GET", "url8", headers={"user-agent": "ua"}) is not None

    auth = client.auth = ("username", "password")
    assert client.make_request("GET", "url9") is not None

    request_mock.assert_has_calls([
        MockCall("GET", "url1", params=None, data=None, headers=None, files=None, json=None,
                 auth=None, timeout=client.timeout),
        MockCall().raise_for_status(),
        MockCall("GET", "url2", params=[("param", "value")], data=None, headers=None, files=None, json=None,
                 auth=None, timeout=client.timeout),
        MockCall().raise_for_status(),
        MockCall("POST", "url3", params=None, data=None, headers=None, files=None, json=None,
                 auth=None, timeout=client.timeout),
        MockCall().raise_for_status(),
        MockCall("POST", "url4", params=None, data=None, headers=None, files=None, json={"param": "value"},
                 auth=None, timeout=client.timeout),
        MockCall().raise_for_status(),
        MockCall("POST", "url5", params=None, data={"param": "value"}, headers=None, files=None, json=None,
                 auth=None, timeout=client.timeout),
        MockCall().raise_for_status(),
        MockCall("POST", "url6", params=None, data=None, headers=None, files={"file": "tuple"}, json=None,
                 auth=None, timeout=client.timeout),
        MockCall().raise_for_status(),
        MockCall("DELETE", "url7", params=None, data=None, headers=None, files=None, json=None,
                 auth=None, timeout=client.timeout),
        MockCall().raise_for_status(),
        MockCall("GET", "url8", params=None, data=None, headers={"user-agent": "ua"}, files=None, json=None,
                 auth=None, timeout=client.timeout),
        MockCall().raise_for_status(),
        MockCall("GET", "url9", params=None, data=None, headers=None, files=None, json=None,
                 auth=auth, timeout=client.timeout),
        MockCall().raise_for_status(),
    ])


def test_make_request_failed(mocker: MockerFixture) -> None:
    """
    must process request errors
    """
    mocker.patch("requests.Session.request", side_effect=Exception())
    logging_mock = mocker.patch("logging.Logger.exception")

    with pytest.raises(Exception):
        SyncHttpClient().make_request("GET", "url")
    logging_mock.assert_called_once()  # we do not check logging arguments


def test_make_request_suppress_errors(mocker: MockerFixture) -> None:
    """
    must suppress request errors correctly
    """
    mocker.patch("requests.Session.request", side_effect=Exception())
    logging_mock = mocker.patch("logging.Logger.exception")

    with pytest.raises(Exception):
        SyncHttpClient().make_request("GET", "url", suppress_errors=True)
    with pytest.raises(Exception):
        SyncHttpClient(suppress_errors=True).make_request("GET", "url")

    logging_mock.assert_not_called()


def test_make_request_session() -> None:
    """
    must use session from arguments
    """
    session_mock = MagicMock()
    client = SyncHttpClient()

    client.make_request("GET", "url", session=session_mock)
    session_mock.request.assert_called_once_with(
        "GET", "url", params=None, data=None, headers=None, files=None, json=None,
        auth=None, timeout=client.timeout)
