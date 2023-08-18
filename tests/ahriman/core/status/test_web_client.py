import json
import logging
import pytest
import requests
import requests_unixsocket

from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.core.configuration import Configuration
from ahriman.core.status.web_client import WebClient
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.internal_status import InternalStatus
from ahriman.models.log_record_id import LogRecordId
from ahriman.models.package import Package
from ahriman.models.user import User


def test_login_url(web_client: WebClient) -> None:
    """
    must generate login url correctly
    """
    assert web_client._login_url.endswith("/api/v1/login")


def test_status_url(web_client: WebClient) -> None:
    """
    must generate package status url correctly
    """
    assert web_client._status_url.endswith("/api/v1/status")


def test_logs_url(web_client: WebClient, package_ahriman: Package) -> None:
    """
    must generate logs url correctly
    """
    assert web_client._logs_url(package_ahriman.base).endswith(f"/api/v1/packages/{package_ahriman.base}/logs")


def test_package_url(web_client: WebClient, package_ahriman: Package) -> None:
    """
    must generate package status url correctly
    """
    assert web_client._package_url("").endswith("/api/v1/packages")
    assert web_client._package_url(package_ahriman.base).endswith(f"/api/v1/packages/{package_ahriman.base}")


def test_parse_address(configuration: Configuration) -> None:
    """
    must extract address correctly
    """
    configuration.set_option("web", "host", "localhost")
    configuration.set_option("web", "port", "8080")
    assert WebClient.parse_address(configuration) == ("http://localhost:8080", False)

    configuration.set_option("web", "address", "http://localhost:8081")
    assert WebClient.parse_address(configuration) == ("http://localhost:8081", False)

    configuration.set_option("web", "unix_socket", "/run/ahriman.sock")
    assert WebClient.parse_address(configuration) == ("http+unix://%2Frun%2Fahriman.sock", True)


def test_create_session(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must create normal requests session
    """
    login_mock = mocker.patch("ahriman.core.status.web_client.WebClient._login")

    session = web_client._create_session(use_unix_socket=False)
    assert isinstance(session, requests.Session)
    assert not isinstance(session, requests_unixsocket.Session)
    login_mock.assert_called_once_with(pytest.helpers.anyvar(int))


def test_create_session_unix_socket(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must create unix socket session
    """
    login_mock = mocker.patch("ahriman.core.status.web_client.WebClient._login")

    session = web_client._create_session(use_unix_socket=True)
    assert isinstance(session, requests_unixsocket.Session)
    login_mock.assert_not_called()


def test_login(web_client: WebClient, user: User, mocker: MockerFixture) -> None:
    """
    must login user
    """
    web_client.user = user
    requests_mock = mocker.patch("requests.Session.request")
    payload = {
        "username": user.username,
        "password": user.password
    }

    web_client._login(requests.Session())
    requests_mock.assert_called_once_with("POST", pytest.helpers.anyvar(str, True),
                                          params=None, json=payload, files=None)


def test_login_failed(web_client: WebClient, user: User, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during login
    """
    web_client.user = user
    mocker.patch("requests.Session.request", side_effect=Exception())
    web_client._login(requests.Session())


def test_login_failed_http_error(web_client: WebClient, user: User, mocker: MockerFixture) -> None:
    """
    must suppress HTTP exception happened during login
    """
    web_client.user = user
    mocker.patch("requests.Session.request", side_effect=requests.exceptions.HTTPError())
    web_client._login(requests.Session())


def test_login_skip(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must skip login if no user set
    """
    requests_mock = mocker.patch("requests.Session.request")
    web_client._login(requests.Session())
    requests_mock.assert_not_called()


def test_make_request(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must make HTTP request
    """
    request_mock = mocker.patch("requests.Session.request")

    assert web_client.make_request("GET", "/url1") is not None
    assert web_client.make_request("GET", "/url2", params=[("param", "value")]) is not None

    assert web_client.make_request("POST", "/url3") is not None
    assert web_client.make_request("POST", "/url4", json={"param": "value"}) is not None
    # we don't want to put full descriptor here
    assert web_client.make_request("POST", "/url5", files={"file": "tuple"}) is not None

    assert web_client.make_request("DELETE", "/url6") is not None

    request_mock.assert_has_calls([
        MockCall("GET", f"{web_client.address}/url1", params=None, json=None, files=None),
        MockCall().raise_for_status(),
        MockCall("GET", f"{web_client.address}/url2", params=[("param", "value")], json=None, files=None),
        MockCall().raise_for_status(),
        MockCall("POST", f"{web_client.address}/url3", params=None, json=None, files=None),
        MockCall().raise_for_status(),
        MockCall("POST", f"{web_client.address}/url4", params=None, json={"param": "value"}, files=None),
        MockCall().raise_for_status(),
        MockCall("POST", f"{web_client.address}/url5", params=None, json=None, files={"file": "tuple"}),
        MockCall().raise_for_status(),
        MockCall("DELETE", f"{web_client.address}/url6", params=None, json=None, files=None),
        MockCall().raise_for_status(),
    ])


def test_make_request_failed(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must make HTTP request
    """
    mocker.patch("requests.Session.request", side_effect=Exception())
    assert web_client.make_request("GET", "url") is None


def test_package_add(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must process package addition
    """
    requests_mock = mocker.patch("requests.Session.request")
    payload = pytest.helpers.get_package_status(package_ahriman)

    web_client.package_add(package_ahriman, BuildStatusEnum.Unknown)
    requests_mock.assert_called_once_with("POST", pytest.helpers.anyvar(str, True),
                                          params=None, json=payload, files=None)


def test_package_add_failed(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during addition
    """
    mocker.patch("requests.Session.request", side_effect=Exception())
    web_client.package_add(package_ahriman, BuildStatusEnum.Unknown)


def test_package_add_failed_http_error(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must suppress HTTP exception happened during addition
    """
    mocker.patch("requests.Session.request", side_effect=requests.exceptions.HTTPError())
    web_client.package_add(package_ahriman, BuildStatusEnum.Unknown)


def test_package_add_failed_suppress(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during addition and don't log
    """
    web_client.suppress_errors = True
    mocker.patch("requests.Session.request", side_effect=Exception())
    logging_mock = mocker.patch("logging.exception")

    web_client.package_add(package_ahriman, BuildStatusEnum.Unknown)
    logging_mock.assert_not_called()


def test_package_add_failed_http_error_suppress(web_client: WebClient, package_ahriman: Package,
                                                mocker: MockerFixture) -> None:
    """
    must suppress HTTP exception happened during addition and don't log
    """
    web_client.suppress_errors = True
    mocker.patch("requests.Session.request", side_effect=requests.exceptions.HTTPError())
    logging_mock = mocker.patch("logging.exception")

    web_client.package_add(package_ahriman, BuildStatusEnum.Unknown)
    logging_mock.assert_not_called()


def test_package_get_all(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return all packages status
    """
    response = [pytest.helpers.get_package_status_extended(package_ahriman)]
    response_obj = requests.Response()
    response_obj._content = json.dumps(response).encode("utf8")
    response_obj.status_code = 200

    requests_mock = mocker.patch("requests.Session.request", return_value=response_obj)

    result = web_client.package_get(None)
    requests_mock.assert_called_once_with("GET", f"{web_client.address}{web_client._package_url()}",
                                          params=None, json=None, files=None)
    assert len(result) == len(response)
    assert (package_ahriman, BuildStatusEnum.Unknown) in [(package, status.status) for package, status in result]


def test_package_get_failed(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during status getting
    """
    mocker.patch("requests.Session.request", side_effect=Exception())
    assert web_client.package_get(None) == []


def test_package_get_failed_http_error(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must suppress HTTP exception happened during status getting
    """
    mocker.patch("requests.Session.request", side_effect=requests.exceptions.HTTPError())
    assert web_client.package_get(None) == []


def test_package_get_single(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return single package status
    """
    response = [pytest.helpers.get_package_status_extended(package_ahriman)]
    response_obj = requests.Response()
    response_obj._content = json.dumps(response).encode("utf8")
    response_obj.status_code = 200

    requests_mock = mocker.patch("requests.Session.request", return_value=response_obj)

    result = web_client.package_get(package_ahriman.base)
    requests_mock.assert_called_once_with("GET",
                                          f"{web_client.address}{web_client._package_url(package_ahriman.base)}",
                                          params=None, json=None, files=None)
    assert len(result) == len(response)
    assert (package_ahriman, BuildStatusEnum.Unknown) in [(package, status.status) for package, status in result]


def test_package_logs(web_client: WebClient, log_record: logging.LogRecord, package_ahriman: Package,
                      mocker: MockerFixture) -> None:
    """
    must process log record
    """
    requests_mock = mocker.patch("requests.Session.request")
    payload = {
        "created": log_record.created,
        "message": log_record.getMessage(),
        "version": package_ahriman.version,
    }

    web_client.package_logs(LogRecordId(package_ahriman.base, package_ahriman.version), log_record)
    requests_mock.assert_called_once_with("POST", pytest.helpers.anyvar(str, True),
                                          params=None, json=payload, files=None)


def test_package_logs_failed(web_client: WebClient, log_record: logging.LogRecord, package_ahriman: Package,
                             mocker: MockerFixture) -> None:
    """
    must pass exception during log post
    """
    mocker.patch("requests.Session.request", side_effect=Exception())
    log_record.package_base = package_ahriman.base
    web_client.package_logs(LogRecordId(package_ahriman.base, package_ahriman.version), log_record)


def test_package_logs_failed_http_error(web_client: WebClient, log_record: logging.LogRecord, package_ahriman: Package,
                                        mocker: MockerFixture) -> None:
    """
    must pass exception during log post
    """
    mocker.patch("requests.Session.request", side_effect=requests.exceptions.HTTPError())
    log_record.package_base = package_ahriman.base
    web_client.package_logs(LogRecordId(package_ahriman.base, package_ahriman.version), log_record)


def test_package_remove(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must process package removal
    """
    requests_mock = mocker.patch("requests.Session.request")

    web_client.package_remove(package_ahriman.base)
    requests_mock.assert_called_once_with("DELETE", pytest.helpers.anyvar(str, True),
                                          params=None, json=None, files=None)


def test_package_remove_failed(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during removal
    """
    mocker.patch("requests.Session.request", side_effect=Exception())
    web_client.package_remove(package_ahriman.base)


def test_package_remove_failed_http_error(web_client: WebClient, package_ahriman: Package,
                                          mocker: MockerFixture) -> None:
    """
    must suppress HTTP exception happened during removal
    """
    mocker.patch("requests.Session.request", side_effect=requests.exceptions.HTTPError())
    web_client.package_remove(package_ahriman.base)


def test_package_update(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must process package update
    """
    requests_mock = mocker.patch("requests.Session.request")

    web_client.package_update(package_ahriman.base, BuildStatusEnum.Unknown)
    requests_mock.assert_called_once_with("POST", pytest.helpers.anyvar(str, True), params=None, json={
        "status": BuildStatusEnum.Unknown.value
    }, files=None)


def test_package_update_failed(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during update
    """
    mocker.patch("requests.Session.request", side_effect=Exception())
    web_client.package_update(package_ahriman.base, BuildStatusEnum.Unknown)


def test_package_update_failed_http_error(web_client: WebClient, package_ahriman: Package,
                                          mocker: MockerFixture) -> None:
    """
    must suppress HTTP exception happened during update
    """
    mocker.patch("requests.Session.request", side_effect=requests.exceptions.HTTPError())
    web_client.package_update(package_ahriman.base, BuildStatusEnum.Unknown)


def test_status_get(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must return web service status
    """
    status = InternalStatus(status=BuildStatus(), architecture="x86_64")
    response_obj = requests.Response()
    response_obj._content = json.dumps(status.view()).encode("utf8")
    response_obj.status_code = 200

    requests_mock = mocker.patch("requests.Session.request", return_value=response_obj)

    result = web_client.status_get()
    requests_mock.assert_called_once_with("GET", f"{web_client.address}{web_client._status_url}",
                                          params=None, json=None, files=None)
    assert result.architecture == "x86_64"


def test_status_get_failed(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during web service status getting
    """
    mocker.patch("requests.Session.request", side_effect=Exception())
    assert web_client.status_get().architecture is None


def test_status_get_failed_http_error(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must suppress HTTP exception happened during web service status getting
    """
    mocker.patch("requests.Session.request", side_effect=requests.exceptions.HTTPError())
    assert web_client.status_get().architecture is None


def test_status_update(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must process service update
    """
    requests_mock = mocker.patch("requests.Session.request")

    web_client.status_update(BuildStatusEnum.Unknown)
    requests_mock.assert_called_once_with("POST", pytest.helpers.anyvar(str, True), params=None, json={
        "status": BuildStatusEnum.Unknown.value
    }, files=None)


def test_status_update_self_failed(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during service update
    """
    mocker.patch("requests.Session.request", side_effect=Exception())
    web_client.status_update(BuildStatusEnum.Unknown)


def test_status_update_failed_http_error(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must suppress HTTP exception happened during service update
    """
    mocker.patch("requests.Session.request", side_effect=requests.exceptions.HTTPError())
    web_client.status_update(BuildStatusEnum.Unknown)
