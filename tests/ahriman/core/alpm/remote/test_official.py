import json
import pytest
import requests

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import MagicMock

from ahriman.core.alpm.remote import Official
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
    return (resource_path_root / "models" / "package_akonadi_aur").read_text()


def test_parse_response(aur_package_akonadi: AURPackage, resource_path_root: Path) -> None:
    """
    must parse success response
    """
    response = _get_response(resource_path_root)
    assert Official.parse_response(json.loads(response)) == [aur_package_akonadi]


def test_parse_response_unknown_error(resource_path_root: Path) -> None:
    """
    must raise exception on invalid response with empty error message
    """
    response = (resource_path_root / "models" / "official_error").read_text()
    with pytest.raises(PackageInfoError, match="API validation error"):
        Official.parse_response(json.loads(response))


def test_remote_git_url(aur_package_akonadi: AURPackage) -> None:
    """
    must generate package git url for core packages
    """
    git_urls = [
        Official.remote_git_url(aur_package_akonadi.package_base, repository)
        for repository in ("core", "extra", "Core", "Extra")
    ]
    assert all(git_url.endswith(f"{aur_package_akonadi.package_base}.git") for git_url in git_urls)
    assert len(set(git_urls)) == 1


def test_remote_web_url(aur_package_akonadi: AURPackage) -> None:
    """
    must generate package git url
    """
    web_url = Official.remote_web_url(aur_package_akonadi.package_base)
    assert web_url.startswith(Official.DEFAULT_ARCHLINUX_URL)


def test_arch_request(official: Official, aur_package_akonadi: AURPackage,
                      mocker: MockerFixture, resource_path_root: Path) -> None:
    """
    must perform request to official repositories
    """
    response_mock = MagicMock()
    response_mock.json.return_value = json.loads(_get_response(resource_path_root))
    request_mock = mocker.patch("ahriman.core.alpm.remote.Official.make_request", return_value=response_mock)

    assert official.arch_request("akonadi", by="q") == [aur_package_akonadi]
    request_mock.assert_called_once_with(
        "GET", "https://archlinux.org/packages/search/json",
        params=[("repo", repository) for repository in Official.DEFAULT_SEARCH_REPOSITORIES] + [("q", "akonadi")])


def test_arch_request_failed(official: Official, mocker: MockerFixture) -> None:
    """
    must reraise generic exception
    """
    mocker.patch("requests.Session.request", side_effect=Exception())
    with pytest.raises(Exception):
        official.arch_request("akonadi", by="q")


def test_arch_request_failed_http_error(official: Official, mocker: MockerFixture) -> None:
    """
    must reraise http exception
    """
    mocker.patch("requests.Session.request", side_effect=requests.HTTPError())
    with pytest.raises(requests.HTTPError):
        official.arch_request("akonadi", by="q")


def test_package_info(official: Official, aur_package_akonadi: AURPackage, mocker: MockerFixture) -> None:
    """
    must make request for info
    """
    request_mock = mocker.patch("ahriman.core.alpm.remote.Official.arch_request",
                                return_value=[aur_package_akonadi])
    assert official.package_info(aur_package_akonadi.name, pacman=None) == aur_package_akonadi
    request_mock.assert_called_once_with(aur_package_akonadi.name, by="name")


def test_package_info_not_found(official: Official, aur_package_ahriman: AURPackage, mocker: MockerFixture) -> None:
    """
    must raise UnknownPackageError in case if no package was found
    """
    mocker.patch("ahriman.core.alpm.remote.Official.arch_request", return_value=[])
    with pytest.raises(UnknownPackageError, match=aur_package_ahriman.name):
        assert official.package_info(aur_package_ahriman.name, pacman=None)


def test_package_search(official: Official, aur_package_akonadi: AURPackage, mocker: MockerFixture) -> None:
    """
    must make request for search
    """
    request_mock = mocker.patch("ahriman.core.alpm.remote.Official.arch_request",
                                return_value=[aur_package_akonadi])
    assert official.package_search(aur_package_akonadi.name, pacman=None, search_by=None) == [
        aur_package_akonadi,
    ]
    request_mock.assert_called_once_with(aur_package_akonadi.name, by="q")


def test_package_search_name(official: Official, aur_package_akonadi: AURPackage, mocker: MockerFixture) -> None:
    """
    must make request for search with custom field
    """
    request_mock = mocker.patch("ahriman.core.alpm.remote.Official.arch_request")
    official.package_search(aur_package_akonadi.name, pacman=None, search_by="name")
    request_mock.assert_called_once_with(aur_package_akonadi.name, by="name")
