import pytest
import requests

from pytest_mock import MockerFixture

from ahriman.core.report.remote_call import RemoteCall
from ahriman.models.result import Result


def test_generate(remote_call: RemoteCall, mocker: MockerFixture) -> None:
    """
    must correctly call client
    """
    update_mock = mocker.patch("ahriman.core.report.remote_call.RemoteCall.remote_update", return_value="id")
    wait_mock = mocker.patch("ahriman.core.report.remote_call.RemoteCall.remote_wait")

    remote_call.generate([], Result())
    update_mock.assert_called_once_with()
    wait_mock.assert_called_once_with("id")


def test_is_process_alive(remote_call: RemoteCall, mocker: MockerFixture) -> None:
    """
    must correctly define if process is alive
    """
    response_obj = requests.Response()
    response_obj._content = """{"is_alive": true}""".encode("utf8")
    response_obj.status_code = 200

    request_mock = mocker.patch("ahriman.core.status.web_client.WebClient.make_request", return_value=response_obj)

    assert remote_call.is_process_alive("id")
    request_mock.assert_called_once_with("GET", "/api/v1/service/process/id")


def test_is_process_alive_unknown(remote_call: RemoteCall, mocker: MockerFixture) -> None:
    """
    must correctly define if process is unknown
    """
    mocker.patch("ahriman.core.status.web_client.WebClient.make_request", return_value=None)
    assert not remote_call.is_process_alive("id")


def test_remote_update(remote_call: RemoteCall, mocker: MockerFixture) -> None:
    """
    must call remote server for update process
    """
    response_obj = requests.Response()
    response_obj._content = """{"process_id": "id"}""".encode("utf8")
    response_obj.status_code = 200

    request_mock = mocker.patch("ahriman.core.status.web_client.WebClient.make_request", return_value=response_obj)

    assert remote_call.remote_update() == "id"
    request_mock.assert_called_once_with("POST", "/api/v1/service/update", json={
        "aur": False,
        "local": False,
        "manual": True,
    })


def test_remote_update_failed(remote_call: RemoteCall, mocker: MockerFixture) -> None:
    """
    must return empty process id in case of errors
    """
    mocker.patch("ahriman.core.status.web_client.WebClient.make_request", return_value=None)
    assert remote_call.generate([], Result()) is None


def test_remote_wait(remote_call: RemoteCall, mocker: MockerFixture) -> None:
    """
    must wait for remote process to success
    """
    wait_mock = mocker.patch("ahriman.models.waiter.Waiter.wait")
    remote_call.remote_wait("id")
    wait_mock.assert_called_once_with(pytest.helpers.anyvar(int), "id")


def test_remote_wait_skip(remote_call: RemoteCall, mocker: MockerFixture) -> None:
    """
    must skip wait if process id is unknown
    """
    wait_mock = mocker.patch("ahriman.models.waiter.Waiter.wait")
    remote_call.remote_wait(None)
    wait_mock.assert_not_called()
