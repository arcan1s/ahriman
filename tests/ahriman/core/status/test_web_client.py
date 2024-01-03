import json
import logging
import pytest
import requests

from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.status.web_client import WebClient
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.changes import Changes
from ahriman.models.internal_status import InternalStatus
from ahriman.models.log_record_id import LogRecordId
from ahriman.models.package import Package


def test_parse_address(configuration: Configuration) -> None:
    """
    must extract address correctly
    """
    configuration.set_option("web", "host", "localhost")
    configuration.set_option("web", "port", "8080")
    assert WebClient.parse_address(configuration) == ("web", "http://localhost:8080")

    configuration.set_option("web", "address", "http://localhost:8081")
    assert WebClient.parse_address(configuration) == ("web", "http://localhost:8081")

    configuration.set_option("web", "unix_socket", "/run/ahriman.sock")
    assert WebClient.parse_address(configuration) == ("web", "http+unix://%2Frun%2Fahriman.sock")

    configuration.set_option("status", "address", "http://localhost:8082")
    assert WebClient.parse_address(configuration) == ("status", "http://localhost:8082")


def test_changes_url(web_client: WebClient, package_ahriman: Package) -> None:
    """
    must generate changes url correctly
    """
    assert web_client._changes_url(package_ahriman.base).startswith(web_client.address)
    assert web_client._changes_url(package_ahriman.base).endswith(f"/api/v1/packages/{package_ahriman.base}/changes")
    assert web_client._changes_url("some/package%name").endswith("/api/v1/packages/some%2Fpackage%25name/changes")


def test_logs_url(web_client: WebClient, package_ahriman: Package) -> None:
    """
    must generate logs url correctly
    """
    assert web_client._logs_url(package_ahriman.base).startswith(web_client.address)
    assert web_client._logs_url(package_ahriman.base).endswith(f"/api/v1/packages/{package_ahriman.base}/logs")
    assert web_client._logs_url("some/package%name").endswith("/api/v1/packages/some%2Fpackage%25name/logs")


def test_package_url(web_client: WebClient, package_ahriman: Package) -> None:
    """
    must generate package status url correctly
    """
    assert web_client._package_url("").startswith(web_client.address)
    assert web_client._package_url("").endswith("/api/v1/packages")

    assert web_client._package_url(package_ahriman.base).startswith(web_client.address)
    assert web_client._package_url(package_ahriman.base).endswith(f"/api/v1/packages/{package_ahriman.base}")
    assert web_client._package_url("some/package%name").endswith("/api/v1/packages/some%2Fpackage%25name")


def test_status_url(web_client: WebClient) -> None:
    """
    must generate package status url correctly
    """
    assert web_client._status_url().startswith(web_client.address)
    assert web_client._status_url().endswith("/api/v1/status")


def test_package_add(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must process package addition
    """
    requests_mock = mocker.patch("ahriman.core.status.web_client.WebClient.make_request")
    payload = pytest.helpers.get_package_status(package_ahriman)

    web_client.package_add(package_ahriman, BuildStatusEnum.Unknown)
    requests_mock.assert_called_once_with("POST", pytest.helpers.anyvar(str, True),
                                          params=web_client.repository_id.query(), json=payload)


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
    mocker.patch("requests.Session.request", side_effect=requests.HTTPError())
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
    mocker.patch("requests.Session.request", side_effect=requests.HTTPError())
    logging_mock = mocker.patch("logging.exception")

    web_client.package_add(package_ahriman, BuildStatusEnum.Unknown)
    logging_mock.assert_not_called()


def test_package_changes_get(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must get changes
    """
    changes = Changes("sha")
    response_obj = requests.Response()
    response_obj._content = json.dumps(changes.view()).encode("utf8")
    response_obj.status_code = 200

    requests_mock = mocker.patch("ahriman.core.status.web_client.WebClient.make_request", return_value=response_obj)

    result = web_client.package_changes_get(package_ahriman.base)
    requests_mock.assert_called_once_with("GET", pytest.helpers.anyvar(str, True),
                                          params=web_client.repository_id.query())
    assert result == changes


def test_package_changes_get_failed(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during changes fetch
    """
    mocker.patch("requests.Session.request", side_effect=Exception())
    web_client.package_changes_get(package_ahriman.base)


def test_package_changes_get_failed_http_error(web_client: WebClient, package_ahriman: Package,
                                               mocker: MockerFixture) -> None:
    """
    must suppress HTTP exception happened during changes fetch
    """
    mocker.patch("requests.Session.request", side_effect=requests.HTTPError())
    web_client.package_changes_get(package_ahriman.base)


def test_package_changes_get_failed_suppress(web_client: WebClient, package_ahriman: Package,
                                             mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during changes fetch and don't log
    """
    web_client.suppress_errors = True
    mocker.patch("requests.Session.request", side_effect=Exception())
    logging_mock = mocker.patch("logging.exception")

    web_client.package_changes_get(package_ahriman.base)
    logging_mock.assert_not_called()


def test_package_changes_get_failed_http_error_suppress(web_client: WebClient, package_ahriman: Package,
                                                        mocker: MockerFixture) -> None:
    """
    must suppress HTTP exception happened during changes fetch and don't log
    """
    web_client.suppress_errors = True
    mocker.patch("requests.Session.request", side_effect=requests.HTTPError())
    logging_mock = mocker.patch("logging.exception")

    web_client.package_changes_get(package_ahriman.base)
    logging_mock.assert_not_called()


def test_package_changes_set(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must set changes
    """
    changes = Changes("sha")
    requests_mock = mocker.patch("ahriman.core.status.web_client.WebClient.make_request")

    web_client.package_changes_set(package_ahriman.base, changes)
    requests_mock.assert_called_once_with("POST", pytest.helpers.anyvar(str, True),
                                          params=web_client.repository_id.query(), json=changes.view())


def test_package_changes_set_failed(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during changes update
    """
    mocker.patch("requests.Session.request", side_effect=Exception())
    web_client.package_changes_set(package_ahriman.base, Changes())


def test_package_changes_set_failed_http_error(web_client: WebClient, package_ahriman: Package,
                                               mocker: MockerFixture) -> None:
    """
    must suppress HTTP exception happened during changes update
    """
    mocker.patch("requests.Session.request", side_effect=requests.HTTPError())
    web_client.package_changes_set(package_ahriman.base, Changes())


def test_package_changes_set_failed_suppress(web_client: WebClient, package_ahriman: Package,
                                             mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during changes update and don't log
    """
    web_client.suppress_errors = True
    mocker.patch("requests.Session.request", side_effect=Exception())
    logging_mock = mocker.patch("logging.exception")

    web_client.package_changes_set(package_ahriman.base, Changes())
    logging_mock.assert_not_called()


def test_package_changes_set_failed_http_error_suppress(web_client: WebClient, package_ahriman: Package,
                                                        mocker: MockerFixture) -> None:
    """
    must suppress HTTP exception happened during changes update and don't log
    """
    web_client.suppress_errors = True
    mocker.patch("requests.Session.request", side_effect=requests.HTTPError())
    logging_mock = mocker.patch("logging.exception")

    web_client.package_changes_set(package_ahriman.base, Changes())
    logging_mock.assert_not_called()


def test_package_get_all(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return all packages status
    """
    response = [pytest.helpers.get_package_status_extended(package_ahriman)]
    response_obj = requests.Response()
    response_obj._content = json.dumps(response).encode("utf8")
    response_obj.status_code = 200

    requests_mock = mocker.patch("ahriman.core.status.web_client.WebClient.make_request",
                                 return_value=response_obj)

    result = web_client.package_get(None)
    requests_mock.assert_called_once_with("GET", web_client._package_url(), params=web_client.repository_id.query())
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
    mocker.patch("requests.Session.request", side_effect=requests.HTTPError())
    assert web_client.package_get(None) == []


def test_package_get_single(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return single package status
    """
    response = [pytest.helpers.get_package_status_extended(package_ahriman)]
    response_obj = requests.Response()
    response_obj._content = json.dumps(response).encode("utf8")
    response_obj.status_code = 200

    requests_mock = mocker.patch("ahriman.core.status.web_client.WebClient.make_request",
                                 return_value=response_obj)

    result = web_client.package_get(package_ahriman.base)
    requests_mock.assert_called_once_with("GET", web_client._package_url(package_ahriman.base),
                                          params=web_client.repository_id.query())
    assert len(result) == len(response)
    assert (package_ahriman, BuildStatusEnum.Unknown) in [(package, status.status) for package, status in result]


def test_package_logs(web_client: WebClient, log_record: logging.LogRecord, package_ahriman: Package,
                      mocker: MockerFixture) -> None:
    """
    must process log record
    """
    requests_mock = mocker.patch("ahriman.core.status.web_client.WebClient.make_request")
    payload = {
        "created": log_record.created,
        "message": log_record.getMessage(),
        "version": package_ahriman.version,
    }

    web_client.package_logs(LogRecordId(package_ahriman.base, package_ahriman.version), log_record)
    requests_mock.assert_called_once_with("POST", pytest.helpers.anyvar(str, True),
                                          params=web_client.repository_id.query(), json=payload, suppress_errors=True)


def test_package_logs_failed(web_client: WebClient, log_record: logging.LogRecord, package_ahriman: Package,
                             mocker: MockerFixture) -> None:
    """
    must pass exception during log post
    """
    mocker.patch("requests.Session.request", side_effect=Exception())
    log_record.package_base = package_ahriman.base
    with pytest.raises(Exception):
        web_client.package_logs(LogRecordId(package_ahriman.base, package_ahriman.version), log_record)


def test_package_logs_failed_http_error(web_client: WebClient, log_record: logging.LogRecord, package_ahriman: Package,
                                        mocker: MockerFixture) -> None:
    """
    must pass exception during log post
    """
    mocker.patch("requests.Session.request", side_effect=requests.HTTPError())
    log_record.package_base = package_ahriman.base
    with pytest.raises(Exception):
        web_client.package_logs(LogRecordId(package_ahriman.base, package_ahriman.version), log_record)


def test_package_remove(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must process package removal
    """
    requests_mock = mocker.patch("ahriman.core.status.web_client.WebClient.make_request")

    web_client.package_remove(package_ahriman.base)
    requests_mock.assert_called_once_with("DELETE", pytest.helpers.anyvar(str, True),
                                          params=web_client.repository_id.query())


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
    mocker.patch("requests.Session.request", side_effect=requests.HTTPError())
    web_client.package_remove(package_ahriman.base)


def test_package_update(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must process package update
    """
    requests_mock = mocker.patch("ahriman.core.status.web_client.WebClient.make_request")

    web_client.package_update(package_ahriman.base, BuildStatusEnum.Unknown)
    requests_mock.assert_called_once_with("POST", pytest.helpers.anyvar(str, True),
                                          params=web_client.repository_id.query(),
                                          json={
                                              "status": BuildStatusEnum.Unknown.value,
    })


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
    mocker.patch("requests.Session.request", side_effect=requests.HTTPError())
    web_client.package_update(package_ahriman.base, BuildStatusEnum.Unknown)


def test_status_get(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must return web service status
    """
    status = InternalStatus(status=BuildStatus(), architecture="x86_64")
    response_obj = requests.Response()
    response_obj._content = json.dumps(status.view()).encode("utf8")
    response_obj.status_code = 200

    requests_mock = mocker.patch("ahriman.core.status.web_client.WebClient.make_request",
                                 return_value=response_obj)

    result = web_client.status_get()
    requests_mock.assert_called_once_with("GET", web_client._status_url(), params=web_client.repository_id.query())
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
    mocker.patch("requests.Session.request", side_effect=requests.HTTPError())
    assert web_client.status_get().architecture is None


def test_status_update(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must process service update
    """
    requests_mock = mocker.patch("ahriman.core.status.web_client.WebClient.make_request")

    web_client.status_update(BuildStatusEnum.Unknown)
    requests_mock.assert_called_once_with(
        "POST", pytest.helpers.anyvar(str, True),
        params=web_client.repository_id.query(),
        json={
            "status": BuildStatusEnum.Unknown.value,
        }
    )


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
    mocker.patch("requests.Session.request", side_effect=requests.HTTPError())
    web_client.status_update(BuildStatusEnum.Unknown)
