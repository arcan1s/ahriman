import pytest

from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.alpm.remote import Remote
from ahriman.models.aur_package import AURPackage


def test_info(pacman: Pacman, mocker: MockerFixture) -> None:
    """
    must call info method
    """
    info_mock = mocker.patch("ahriman.core.alpm.remote.Remote.package_info")
    Remote.info("ahriman", pacman=pacman)
    info_mock.assert_called_once_with("ahriman", pacman=pacman)


def test_multisearch(aur_package_ahriman: AURPackage, pacman: Pacman, mocker: MockerFixture) -> None:
    """
    must search in AUR with multiple words
    """
    terms = ["ahriman", "is", "cool"]
    search_mock = mocker.patch("ahriman.core.alpm.remote.Remote.search", return_value=[aur_package_ahriman])

    assert Remote.multisearch(*terms, pacman=pacman) == [aur_package_ahriman]
    search_mock.assert_has_calls([MockCall("ahriman", pacman=pacman), MockCall("cool", pacman=pacman)])


def test_multisearch_empty(pacman: Pacman, mocker: MockerFixture) -> None:
    """
    must return empty list if no long terms supplied
    """
    terms = ["it", "is"]
    search_mock = mocker.patch("ahriman.core.alpm.remote.Remote.search")

    assert Remote.multisearch(*terms, pacman=pacman) == []
    search_mock.assert_not_called()


def test_multisearch_single(aur_package_ahriman: AURPackage, pacman: Pacman, mocker: MockerFixture) -> None:
    """
    must search in AUR with one word
    """
    search_mock = mocker.patch("ahriman.core.alpm.remote.Remote.search", return_value=[aur_package_ahriman])
    assert Remote.multisearch("ahriman", pacman=pacman) == [aur_package_ahriman]
    search_mock.assert_called_once_with("ahriman", pacman=pacman)


def test_remote_git_url(remote: Remote, pacman: Pacman) -> None:
    """
    must raise NotImplemented for missing remote git url
    """
    with pytest.raises(NotImplementedError):
        remote.remote_git_url("package", "repositorys")


def test_remote_web_url(remote: Remote, pacman: Pacman) -> None:
    """
    must raise NotImplemented for missing remote web url
    """
    with pytest.raises(NotImplementedError):
        remote.remote_web_url("package")


def test_search(pacman: Pacman, mocker: MockerFixture) -> None:
    """
    must call search method
    """
    search_mock = mocker.patch("ahriman.core.alpm.remote.Remote.package_search")
    Remote.search("ahriman", pacman=pacman)
    search_mock.assert_called_once_with("ahriman", pacman=pacman)


def test_package_info(remote: Remote, pacman: Pacman) -> None:
    """
    must raise NotImplemented for missing package info method
    """
    with pytest.raises(NotImplementedError):
        remote.package_info("package", pacman=pacman)


def test_package_search(remote: Remote, pacman: Pacman) -> None:
    """
    must raise NotImplemented for missing package search method
    """
    with pytest.raises(NotImplementedError):
        remote.package_search("package", pacman=pacman)
