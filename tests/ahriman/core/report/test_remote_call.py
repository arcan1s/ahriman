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
    request_mock.assert_called_once_with("GET", f"{remote_call.client.address}/api/v1/service/process/id")


def test_is_process_alive_unknown(remote_call: RemoteCall, mocker: MockerFixture) -> None:
    """
    must correctly define if process is unknown
    """
    response = requests.Response()
    response.status_code = 404
    mocker.patch("ahriman.core.status.web_client.WebClient.make_request",
                 side_effect=requests.HTTPError(response=response))

    assert not remote_call.is_process_alive("id")


def test_is_process_alive_error(remote_call: RemoteCall, mocker: MockerFixture) -> None:
    """
    must reraise exception on process request
    """
    mocker.patch("ahriman.core.status.web_client.WebClient.make_request", side_effect=Exception)

    with pytest.raises(Exception):
        remote_call.is_process_alive("id")


def test_is_process_alive_http_error(remote_call: RemoteCall, mocker: MockerFixture) -> None:
    """
    must reraise http exception on process request
    """
    response = requests.Response()
    response.status_code = 500
    mocker.patch("ahriman.core.status.web_client.WebClient.make_request",
                 side_effect=requests.HTTPError(response=response))

    with pytest.raises(requests.HTTPError):
        remote_call.is_process_alive("id")


def test_remote_update(remote_call: RemoteCall, mocker: MockerFixture) -> None:
    """
    must call remote server for update process
    """
    response_obj = requests.Response()
    response_obj._content = """{"process_id": "id"}""".encode("utf8")
    response_obj.status_code = 200

    request_mock = mocker.patch("ahriman.core.status.web_client.WebClient.make_request", return_value=response_obj)

    assert remote_call.remote_update() == "id"
    request_mock.assert_called_once_with("POST", f"{remote_call.client.address}/api/v1/service/update",
                                         params=remote_call.repository_id.query(),
                                         json={
                                             "aur": False,
                                             "local": False,
                                             "manual": True,
                                         })


def test_remote_wait(remote_call: RemoteCall, mocker: MockerFixture) -> None:
    """
    must wait for remote process to success
    """
    wait_mock = mocker.patch("ahriman.models.waiter.Waiter.wait")
    remote_call.remote_wait("id")
    wait_mock.assert_called_once_with(pytest.helpers.anyvar(int), "id")
