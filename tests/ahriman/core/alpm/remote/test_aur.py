import json
import pytest
import requests

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import MagicMock

from ahriman.core.alpm.remote import AUR
from ahriman.core.exceptions import PackageInfoError, UnknownPackageError
from ahriman.models.aur_package import AURPackage


def _get_response(resource_path_root: Path) -> str:
    """
    load response from resource file

    Args:
        resource_path_root(Path): path to resource root

    Returns:
        str: response text
    """
    return (resource_path_root / "models" / "package_ahriman_aur").read_text()


def test_parse_response(aur_package_ahriman: AURPackage, resource_path_root: Path) -> None:
    """
    must parse success response
    """
    response = _get_response(resource_path_root)
    assert AUR.parse_response(json.loads(response)) == [aur_package_ahriman]


def test_parse_response_error(resource_path_root: Path) -> None:
    """
    must raise exception on invalid response
    """
    response = (resource_path_root / "models" / "aur_error").read_text()
    with pytest.raises(PackageInfoError, match="Incorrect request type specified."):
        AUR.parse_response(json.loads(response))


def test_parse_response_unknown_error() -> None:
    """
    must raise exception on invalid response with empty error message
    """
    with pytest.raises(PackageInfoError, match="Unknown API error"):
        AUR.parse_response({"type": "error"})


def test_remote_git_url(aur_package_ahriman: AURPackage) -> None:
    """
    must generate package git url
    """
    git_url = AUR.remote_git_url(aur_package_ahriman.package_base, aur_package_ahriman.repository)
    assert git_url.endswith(".git")
    assert git_url.startswith(AUR.DEFAULT_AUR_URL)


def test_remote_web_url(aur_package_ahriman: AURPackage) -> None:
    """
    must generate package web url
    """
    web_url = AUR.remote_web_url(aur_package_ahriman.package_base)
    assert web_url.startswith(AUR.DEFAULT_AUR_URL)


def test_aur_request(aur: AUR, aur_package_ahriman: AURPackage,
                     mocker: MockerFixture, resource_path_root: Path) -> None:
    """
    must perform request to AUR
    """
    response_mock = MagicMock()
    response_mock.json.return_value = json.loads(_get_response(resource_path_root))
    request_mock = mocker.patch("ahriman.core.alpm.remote.AUR.make_request", return_value=response_mock)

    assert aur.aur_request("info", "ahriman") == [aur_package_ahriman]
    request_mock.assert_called_once_with(
        "GET", "https://aur.archlinux.org/rpc",
        params=[("type", "info"), ("v", "5"), ("arg", "ahriman")])


def test_aur_request_multi_arg(aur: AUR, aur_package_ahriman: AURPackage,
                               mocker: MockerFixture, resource_path_root: Path) -> None:
    """
    must perform request to AUR with multiple args
    """
    response_mock = MagicMock()
    response_mock.json.return_value = json.loads(_get_response(resource_path_root))
    request_mock = mocker.patch("ahriman.core.alpm.remote.AUR.make_request", return_value=response_mock)

    assert aur.aur_request("search", "ahriman", "is", "cool") == [aur_package_ahriman]
    request_mock.assert_called_once_with(
        "GET", "https://aur.archlinux.org/rpc",
        params=[("type", "search"), ("v", "5"), ("arg[]", "ahriman"), ("arg[]", "is"), ("arg[]", "cool")])


def test_aur_request_with_kwargs(aur: AUR, aur_package_ahriman: AURPackage,
                                 mocker: MockerFixture, resource_path_root: Path) -> None:
    """
    must perform request to AUR with named parameters
    """
    response_mock = MagicMock()
    response_mock.json.return_value = json.loads(_get_response(resource_path_root))
    request_mock = mocker.patch("ahriman.core.alpm.remote.AUR.make_request", return_value=response_mock)

    assert aur.aur_request("search", "ahriman", by="name") == [aur_package_ahriman]
    request_mock.assert_called_once_with(
        "GET", "https://aur.archlinux.org/rpc",
        params=[("type", "search"), ("v", "5"), ("arg", "ahriman"), ("by", "name")])


def test_aur_request_failed(aur: AUR, mocker: MockerFixture) -> None:
    """
    must reraise generic exception
    """
    mocker.patch("requests.Session.request", side_effect=Exception())
    with pytest.raises(Exception):
        aur.aur_request("info", "ahriman")


def test_aur_request_failed_http_error(aur: AUR, mocker: MockerFixture) -> None:
    """    must reraise http exception
    """
    mocker.patch("requests.Session.request", side_effect=requests.HTTPError())
    with pytest.raises(requests.HTTPError):
        aur.aur_request("info", "ahriman")


def test_package_info(aur: AUR, aur_package_ahriman: AURPackage, mocker: MockerFixture) -> None:
    """
    must make request for info
    """
    request_mock = mocker.patch("ahriman.core.alpm.remote.AUR.aur_request", return_value=[aur_package_ahriman])
    assert aur.package_info(aur_package_ahriman.name, pacman=None) == aur_package_ahriman
    request_mock.assert_called_once_with("info", aur_package_ahriman.name)


def test_package_info_not_found(aur: AUR, aur_package_ahriman: AURPackage, mocker: MockerFixture) -> None:
    """
    must raise UnknownPackage exception in case if no package was found
    """
    mocker.patch("ahriman.core.alpm.remote.AUR.aur_request", return_value=[])
    with pytest.raises(UnknownPackageError, match=aur_package_ahriman.name):
        assert aur.package_info(aur_package_ahriman.name, pacman=None)


def test_package_search(aur: AUR, aur_package_ahriman: AURPackage, mocker: MockerFixture) -> None:
    """
    must make request for search
    """
    request_mock = mocker.patch("ahriman.core.alpm.remote.AUR.aur_request", return_value=[aur_package_ahriman])
    assert aur.package_search(aur_package_ahriman.name, pacman=None) == [aur_package_ahriman]
    request_mock.assert_called_once_with("search", aur_package_ahriman.name, by="name-desc")
