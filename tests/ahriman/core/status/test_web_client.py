import json
import pytest
import requests

from pytest_mock import MockerFixture
from requests import Response

from ahriman.core.status.web_client import WebClient
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.internal_status import InternalStatus
from ahriman.models.package import Package


def test_ahriman_url(web_client: WebClient) -> None:
    """
    must generate service status url correctly
    """
    assert web_client._ahriman_url().startswith(f"http://{web_client.host}:{web_client.port}")
    assert web_client._ahriman_url().endswith("/api/v1/ahriman")


def test_package_url(web_client: WebClient, package_ahriman: Package) -> None:
    """
    must generate package status correctly
    """
    assert web_client._package_url(package_ahriman.base).startswith(f"http://{web_client.host}:{web_client.port}")
    assert web_client._package_url(package_ahriman.base).endswith(f"/api/v1/packages/{package_ahriman.base}")


def test_status_url(web_client: WebClient) -> None:
    """
    must generate service status url correctly
    """
    assert web_client._status_url().startswith(f"http://{web_client.host}:{web_client.port}")
    assert web_client._status_url().endswith("/api/v1/status")


def test_add(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must process package addition
    """
    requests_mock = mocker.patch("requests.post")
    payload = pytest.helpers.get_package_status(package_ahriman)

    web_client.add(package_ahriman, BuildStatusEnum.Unknown)
    requests_mock.assert_called_with(pytest.helpers.anyvar(str, True), json=payload)


def test_add_failed(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during addition
    """
    mocker.patch("requests.post", side_effect=Exception())
    web_client.add(package_ahriman, BuildStatusEnum.Unknown)


def test_add_failed_http_error(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during addition
    """
    mocker.patch("requests.post", side_effect=requests.exceptions.HTTPError())
    web_client.add(package_ahriman, BuildStatusEnum.Unknown)


def test_get_all(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return all packages status
    """
    response = [pytest.helpers.get_package_status_extended(package_ahriman)]
    response_obj = Response()
    response_obj._content = json.dumps(response).encode("utf8")
    response_obj.status_code = 200

    requests_mock = mocker.patch("requests.get", return_value=response_obj)

    result = web_client.get(None)
    requests_mock.assert_called_once()
    assert len(result) == len(response)
    assert (package_ahriman, BuildStatusEnum.Unknown) in [(package, status.status) for package, status in result]


def test_get_failed(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during status getting
    """
    mocker.patch("requests.get", side_effect=Exception())
    assert web_client.get(None) == []


def test_get_failed_http_error(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during status getting
    """
    mocker.patch("requests.get", side_effect=requests.exceptions.HTTPError())
    assert web_client.get(None) == []


def test_get_single(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return single package status
    """
    response = [pytest.helpers.get_package_status_extended(package_ahriman)]
    response_obj = Response()
    response_obj._content = json.dumps(response).encode("utf8")
    response_obj.status_code = 200

    requests_mock = mocker.patch("requests.get", return_value=response_obj)

    result = web_client.get(package_ahriman.base)
    requests_mock.assert_called_once()
    assert len(result) == len(response)
    assert (package_ahriman, BuildStatusEnum.Unknown) in [(package, status.status) for package, status in result]


def test_get_internal(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must return web service status
    """
    response_obj = Response()
    response_obj._content = json.dumps(InternalStatus(architecture="x86_64").view()).encode("utf8")
    response_obj.status_code = 200

    requests_mock = mocker.patch("requests.get", return_value=response_obj)

    result = web_client.get_internal()
    requests_mock.assert_called_once()
    assert result.architecture == "x86_64"


def test_get_internal_failed(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during web service status getting
    """
    mocker.patch("requests.get", side_effect=Exception())
    assert web_client.get_internal() == InternalStatus()


def test_get_internal_failed_http_error(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during web service status getting
    """
    mocker.patch("requests.get", side_effect=requests.exceptions.HTTPError())
    assert web_client.get_internal() == InternalStatus()


def test_get_self(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must return service status
    """
    response_obj = Response()
    response_obj._content = json.dumps(BuildStatus().view()).encode("utf8")
    response_obj.status_code = 200

    requests_mock = mocker.patch("requests.get", return_value=response_obj)

    result = web_client.get_self()
    requests_mock.assert_called_once()
    assert result.status == BuildStatusEnum.Unknown


def test_get_self_failed(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during service status getting
    """
    mocker.patch("requests.get", side_effect=Exception())
    assert web_client.get_self().status == BuildStatusEnum.Unknown


def test_get_self_failed_http_error(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during service status getting
    """
    mocker.patch("requests.get", side_effect=requests.exceptions.HTTPError())
    assert web_client.get_self().status == BuildStatusEnum.Unknown


def test_remove(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must process package removal
    """
    requests_mock = mocker.patch("requests.delete")

    web_client.remove(package_ahriman.base)
    requests_mock.assert_called_with(pytest.helpers.anyvar(str, True))


def test_remove_failed(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during removal
    """
    mocker.patch("requests.delete", side_effect=Exception())
    web_client.remove(package_ahriman.base)


def test_remove_failed_http_error(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during removal
    """
    mocker.patch("requests.delete", side_effect=requests.exceptions.HTTPError())
    web_client.remove(package_ahriman.base)


def test_update(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must process package update
    """
    requests_mock = mocker.patch("requests.post")

    web_client.update(package_ahriman.base, BuildStatusEnum.Unknown)
    requests_mock.assert_called_with(pytest.helpers.anyvar(str, True), json={"status": BuildStatusEnum.Unknown.value})


def test_update_failed(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during update
    """
    mocker.patch("requests.post", side_effect=Exception())
    web_client.update(package_ahriman.base, BuildStatusEnum.Unknown)


def test_update_failed_http_error(web_client: WebClient, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during update
    """
    mocker.patch("requests.post", side_effect=requests.exceptions.HTTPError())
    web_client.update(package_ahriman.base, BuildStatusEnum.Unknown)


def test_update_self(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must process service update
    """
    requests_mock = mocker.patch("requests.post")

    web_client.update_self(BuildStatusEnum.Unknown)
    requests_mock.assert_called_with(pytest.helpers.anyvar(str, True), json={"status": BuildStatusEnum.Unknown.value})


def test_update_self_failed(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during service update
    """
    mocker.patch("requests.post", side_effect=Exception())
    web_client.update_self(BuildStatusEnum.Unknown)


def test_update_self_failed_http_error(web_client: WebClient, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during service update
    """
    mocker.patch("requests.post", side_effect=requests.exceptions.HTTPError())
    web_client.update_self(BuildStatusEnum.Unknown)
