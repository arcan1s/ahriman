import json
import pytest
import requests

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import MagicMock

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.alpm.remote.official import Official
from ahriman.core.exceptions import InvalidPackageInfo
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
    with pytest.raises(InvalidPackageInfo, match="API validation error"):
        Official.parse_response(json.loads(response))


def test_remote_git_url(aur_package_akonadi: AURPackage) -> None:
    """
    must generate package git url for core packages
    """
    git_urls = [
        Official.remote_git_url(aur_package_akonadi.package_base, repository)
        for repository in ("core", "extra", "Core", "Extra")
    ]
    assert all(git_url.endswith("svntogit-packages.git") for git_url in git_urls)
    assert len(set(git_urls)) == 1


def test_remote_git_url_community(aur_package_akonadi: AURPackage) -> None:
    """
    must generate package git url for core packages
    """
    git_urls = [
        Official.remote_git_url(aur_package_akonadi.package_base, repository)
        for repository in ("community", "multilib", "Community", "Multilib")
    ]
    assert all(git_url.endswith("svntogit-community.git") for git_url in git_urls)
    assert len(set(git_urls)) == 1


def test_remote_web_url(aur_package_akonadi: AURPackage) -> None:
    """
    must generate package git url
    """
    web_url = Official.remote_web_url(aur_package_akonadi.package_base)
    assert web_url.startswith(Official.DEFAULT_ARCHLINUX_URL)


def test_make_request(official: Official, aur_package_akonadi: AURPackage,
                      mocker: MockerFixture, resource_path_root: Path) -> None:
    """
    must perform request to official repositories
    """
    response_mock = MagicMock()
    response_mock.json.return_value = json.loads(_get_response(resource_path_root))
    request_mock = mocker.patch("requests.get", return_value=response_mock)

    assert official.make_request("akonadi", by="q") == [aur_package_akonadi]
    request_mock.assert_called_once_with("https://archlinux.org/packages/search/json",
                                         params={"q": ("akonadi",), "repo": Official.DEFAULT_SEARCH_REPOSITORIES})


def test_make_request_failed(official: Official, mocker: MockerFixture) -> None:
    """
    must reraise generic exception
    """
    mocker.patch("requests.get", side_effect=Exception())
    with pytest.raises(Exception):
        official.make_request("akonadi", by="q")


def test_make_request_failed_http_error(official: Official, mocker: MockerFixture) -> None:
    """
    must reraise http exception
    """
    mocker.patch("requests.get", side_effect=requests.exceptions.HTTPError())
    with pytest.raises(requests.exceptions.HTTPError):
        official.make_request("akonadi", by="q")


def test_package_info(official: Official, aur_package_akonadi: AURPackage, pacman: Pacman,
                      mocker: MockerFixture) -> None:
    """
    must make request for info
    """
    request_mock = mocker.patch("ahriman.core.alpm.remote.official.Official.make_request",
                                return_value=[aur_package_akonadi])
    assert official.package_info(aur_package_akonadi.name, pacman=pacman) == aur_package_akonadi
    request_mock.assert_called_once_with(aur_package_akonadi.name, by="name")


def test_package_search(official: Official, aur_package_akonadi: AURPackage, pacman: Pacman,
                        mocker: MockerFixture) -> None:
    """
    must make request for search
    """
    request_mock = mocker.patch("ahriman.core.alpm.remote.official.Official.make_request",
                                return_value=[aur_package_akonadi])
    assert official.package_search(aur_package_akonadi.name, pacman=pacman) == [aur_package_akonadi]
    request_mock.assert_called_once_with(aur_package_akonadi.name, by="q")
