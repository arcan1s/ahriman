import json
import logging
import pytest
import requests
import requests_unixsocket

from pytest_mock import MockerFixture
from requests import Response

from ahriman.core.configuration import Configuration
from ahriman.core.status.web_client import WebClient
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.internal_status import InternalStatus
from ahriman.models.package import Package
from ahriman.models.user import User


def test_login_url(web_client: WebClient) -> None:
    """
    must generate login url correctly
    """
    assert web_client._login_url.startswith(web_client.address)
    assert web_client._login_url.endswith("/api/v1/login")


def test_status_url(web_client: WebClient) -> None:
    """
    must generate package status url correctly
    """
    assert web_client._status_url.startswith(web_client.address)
    assert web_client._status_url.endswith("/api/v1/status")


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
    login_mock.assert_called_once_with()


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
    requests_mock = mocker.patch("requests.Session.post")
    payload = {
        "username": user.username,
        "password": user.password
    }

    web_client._login()
    requests_mock.assert_called_once_with(pytest.helpers.anyvar(str, True), json=payload)


def test_login_failed(web_client: WebClient, user: User, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during login
    """
    web_client.user = user
    mocker.patch("requests.Session.post", side_effect=Exception())
    web_client._login()


def test_login_failed_http_error(web_client: WebClient, user: User, mocker: MockerFixture) -> None:
    """
    must suppress HTTP exception happened during login
    """
    web_client.user = user
    mocker.patch("requests.Session.post", side_effect=requests.exceptions.HTTPError())
    web_client._login()


def test_login_skip(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must skip login if no user set
    """
    requests_mock = mocker.patch("requests.Session.post")
    web_client._login()
    requests_mock.assert_not_called()


def test_logs_url(web_client: WebClient, package_ahriman: Package) -> None:
    """
    must generate logs url correctly
    """
    assert web_client._logs_url(package_ahriman.base).startswith(web_client.address)
    assert web_client._logs_url(package_ahriman.base).endswith(f"/api/v1/packages/{package_ahriman.base}/logs")


def test_package_url(web_client: WebClient, package_ahriman: Package) -> None:
    """
    must generate package status url correctly
    """
    assert web_client._package_url("").startswith(web_client.address)
    assert web_client._package_url("").endswith(f"/api/v1/packages")

    assert web_client._package_url(package_ahriman.base).startswith(web_client.address)
    assert web_client._package_url(package_ahriman.base).endswith(f"/api/v1/packages/{package_ahriman.base}")


def test_add(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must process package addition
    """
    requests_mock = mocker.patch("requests.Session.post")
    payload = pytest.helpers.get_package_status(package_ahriman)

    web_client.add(package_ahriman, BuildStatusEnum.Unknown)
    requests_mock.assert_called_once_with(pytest.helpers.anyvar(str, True), json=payload)


def test_add_failed(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during addition
    """
    mocker.patch("requests.Session.post", side_effect=Exception())
    web_client.add(package_ahriman, BuildStatusEnum.Unknown)


def test_add_failed_http_error(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must suppress HTTP exception happened during addition
    """
    mocker.patch("requests.Session.post", side_effect=requests.exceptions.HTTPError())
    web_client.add(package_ahriman, BuildStatusEnum.Unknown)


def test_add_failed_suppress(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during addition and don't log
    """
    web_client.suppress_errors = True
    mocker.patch("requests.Session.post", side_effect=Exception())
    logging_mock = mocker.patch("logging.exception")

    web_client.add(package_ahriman, BuildStatusEnum.Unknown)
    logging_mock.assert_not_called()


def test_add_failed_http_error_suppress(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must suppress HTTP exception happened during addition and don't log
    """
    web_client.suppress_errors = True
    mocker.patch("requests.Session.post", side_effect=requests.exceptions.HTTPError())
    logging_mock = mocker.patch("logging.exception")

    web_client.add(package_ahriman, BuildStatusEnum.Unknown)
    logging_mock.assert_not_called()


def test_get_all(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return all packages status
    """
    response = [pytest.helpers.get_package_status_extended(package_ahriman)]
    response_obj = Response()
    response_obj._content = json.dumps(response).encode("utf8")
    response_obj.status_code = 200

    requests_mock = mocker.patch("requests.Session.get", return_value=response_obj)

    result = web_client.get(None)
    requests_mock.assert_called_once_with(web_client._package_url())
    assert len(result) == len(response)
    assert (package_ahriman, BuildStatusEnum.Unknown) in [(package, status.status) for package, status in result]


def test_get_failed(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during status getting
    """
    mocker.patch("requests.Session.get", side_effect=Exception())
    assert web_client.get(None) == []


def test_get_failed_http_error(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must suppress HTTP exception happened during status getting
    """
    mocker.patch("requests.Session.get", side_effect=requests.exceptions.HTTPError())
    assert web_client.get(None) == []


def test_get_single(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return single package status
    """
    response = [pytest.helpers.get_package_status_extended(package_ahriman)]
    response_obj = Response()
    response_obj._content = json.dumps(response).encode("utf8")
    response_obj.status_code = 200

    requests_mock = mocker.patch("requests.Session.get", return_value=response_obj)

    result = web_client.get(package_ahriman.base)
    requests_mock.assert_called_once_with(web_client._package_url(package_ahriman.base))
    assert len(result) == len(response)
    assert (package_ahriman, BuildStatusEnum.Unknown) in [(package, status.status) for package, status in result]


def test_get_internal(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must return web service status
    """
    status = InternalStatus(status=BuildStatus(), architecture="x86_64")
    response_obj = Response()
    response_obj._content = json.dumps(status.view()).encode("utf8")
    response_obj.status_code = 200

    requests_mock = mocker.patch("requests.Session.get", return_value=response_obj)

    result = web_client.get_internal()
    requests_mock.assert_called_once_with(web_client._status_url)
    assert result.architecture == "x86_64"


def test_get_internal_failed(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during web service status getting
    """
    mocker.patch("requests.Session.get", side_effect=Exception())
    assert web_client.get_internal().architecture is None


def test_get_internal_failed_http_error(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must suppress HTTP exception happened during web service status getting
    """
    mocker.patch("requests.Session.get", side_effect=requests.exceptions.HTTPError())
    assert web_client.get_internal().architecture is None


def test_logs(web_client: WebClient, log_record: logging.LogRecord, package_ahriman: Package,
              mocker: MockerFixture) -> None:
    """
    must process log record
    """
    requests_mock = mocker.patch("requests.Session.post")
    payload = {
        "created": log_record.created,
        "message": log_record.getMessage(),
        "process_id": log_record.process,
    }

    web_client.logs(package_ahriman.base, log_record)
    requests_mock.assert_called_once_with(pytest.helpers.anyvar(str, True), json=payload)


def test_log_failed(web_client: WebClient, log_record: logging.LogRecord, package_ahriman: Package,
                    mocker: MockerFixture) -> None:
    """
    must pass exception during log post
    """
    mocker.patch("requests.Session.post", side_effect=Exception())
    log_record.package_base = package_ahriman.base
    with pytest.raises(Exception):
        web_client.logs(package_ahriman.base, log_record)


def test_remove(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must process package removal
    """
    requests_mock = mocker.patch("requests.Session.delete")

    web_client.remove(package_ahriman.base)
    requests_mock.assert_called_once_with(pytest.helpers.anyvar(str, True))


def test_remove_failed(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during removal
    """
    mocker.patch("requests.Session.delete", side_effect=Exception())
    web_client.remove(package_ahriman.base)


def test_remove_failed_http_error(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must suppress HTTP exception happened during removal
    """
    mocker.patch("requests.Session.delete", side_effect=requests.exceptions.HTTPError())
    web_client.remove(package_ahriman.base)


def test_update(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must process package update
    """
    requests_mock = mocker.patch("requests.Session.post")

    web_client.update(package_ahriman.base, BuildStatusEnum.Unknown)
    requests_mock.assert_called_once_with(pytest.helpers.anyvar(str, True), json={
                                          "status": BuildStatusEnum.Unknown.value})


def test_update_failed(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during update
    """
    mocker.patch("requests.Session.post", side_effect=Exception())
    web_client.update(package_ahriman.base, BuildStatusEnum.Unknown)


def test_update_failed_http_error(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must suppress HTTP exception happened during update
    """
    mocker.patch("requests.Session.post", side_effect=requests.exceptions.HTTPError())
    web_client.update(package_ahriman.base, BuildStatusEnum.Unknown)


def test_update_self(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must process service update
    """
    requests_mock = mocker.patch("requests.Session.post")

    web_client.update_self(BuildStatusEnum.Unknown)
    requests_mock.assert_called_once_with(pytest.helpers.anyvar(str, True), json={
                                          "status": BuildStatusEnum.Unknown.value})


def test_update_self_failed(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during service update
    """
    mocker.patch("requests.Session.post", side_effect=Exception())
    web_client.update_self(BuildStatusEnum.Unknown)


def test_update_self_failed_http_error(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must suppress HTTP exception happened during service update
    """
    mocker.patch("requests.Session.post", side_effect=requests.exceptions.HTTPError())
    web_client.update_self(BuildStatusEnum.Unknown)
