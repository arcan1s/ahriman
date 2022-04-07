import pytest

from pytest_mock import MockerFixture
from unittest import mock

from ahriman.core.alpm.remote.remote import Remote
from ahriman.models.aur_package import AURPackage


def test_info(mocker: MockerFixture) -> None:
    """
    must call info method
    """
    info_mock = mocker.patch("ahriman.core.alpm.remote.remote.Remote.package_info")
    Remote.info("ahriman")
    info_mock.assert_called_once_with("ahriman")


def test_multisearch(aur_package_ahriman: AURPackage, mocker: MockerFixture) -> None:
    """
    must search in AUR with multiple words
    """
    terms = ["ahriman", "is", "cool"]
    search_mock = mocker.patch("ahriman.core.alpm.remote.remote.Remote.search", return_value=[aur_package_ahriman])

    assert Remote.multisearch(*terms) == [aur_package_ahriman]
    search_mock.assert_has_calls([mock.call("ahriman"), mock.call("cool")])


def test_multisearch_empty(mocker: MockerFixture) -> None:
    """
    must return empty list if no long terms supplied
    """
    terms = ["it", "is"]
    search_mock = mocker.patch("ahriman.core.alpm.remote.remote.Remote.search")

    assert Remote.multisearch(*terms) == []
    search_mock.assert_not_called()


def test_multisearch_single(aur_package_ahriman: AURPackage, mocker: MockerFixture) -> None:
    """
    must search in AUR with one word
    """
    search_mock = mocker.patch("ahriman.core.alpm.remote.remote.Remote.search", return_value=[aur_package_ahriman])
    assert Remote.multisearch("ahriman") == [aur_package_ahriman]
    search_mock.assert_called_once_with("ahriman")


def test_search(mocker: MockerFixture) -> None:
    """
    must call search method
    """
    search_mock = mocker.patch("ahriman.core.alpm.remote.remote.Remote.package_search")
    Remote.search("ahriman")
    search_mock.assert_called_once_with("ahriman")


def test_package_info(remote: Remote) -> None:
    """
    must raise NotImplemented for missing package info method
    """
    with pytest.raises(NotImplementedError):
        remote.package_info("package")


def test_package_search(remote: Remote) -> None:
    """
    must raise NotImplemented for missing package search method
    """
    with pytest.raises(NotImplementedError):
        remote.package_search("package")
