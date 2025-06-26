import pytest

from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.alpm.remote import Remote
from ahriman.core.exceptions import UnknownPackageError
from ahriman.models.aur_package import AURPackage


def test_info(aur_package_ahriman: AURPackage, pacman: Pacman, mocker: MockerFixture) -> None:
    """
    must call info method
    """
    info_mock = mocker.patch("ahriman.core.alpm.remote.Remote.package_info", return_value=aur_package_ahriman)
    assert Remote.info(aur_package_ahriman.name, pacman=pacman) == aur_package_ahriman
    info_mock.assert_called_once_with(aur_package_ahriman.name, pacman=pacman)


def test_info_not_found(aur_package_ahriman: AURPackage, pacman: Pacman, mocker: MockerFixture) -> None:
    """
    must raise UnknownPackageError if no package found and search by provides is disabled
    """
    mocker.patch("ahriman.core.alpm.remote.Remote.package_info",
                 side_effect=UnknownPackageError(aur_package_ahriman.name))
    with pytest.raises(UnknownPackageError):
        Remote.info(aur_package_ahriman.name, pacman=pacman)


def test_info_include_provides(aur_package_ahriman: AURPackage, pacman: Pacman, mocker: MockerFixture) -> None:
    """
    must perform search through provides list is set
    """
    mocker.patch("ahriman.core.alpm.remote.Remote.package_info",
                 side_effect=UnknownPackageError(aur_package_ahriman.name))
    provided_mock = mocker.patch("ahriman.core.alpm.remote.Remote.package_provided_by",
                                 return_value=[aur_package_ahriman])

    assert Remote.info(aur_package_ahriman.name, pacman=pacman, include_provides=True) == aur_package_ahriman
    provided_mock.assert_called_once_with(aur_package_ahriman.name, pacman=pacman)


def test_info_include_provides_not_found(aur_package_ahriman: AURPackage, pacman: Pacman,
                                         mocker: MockerFixture) -> None:
    """
    must raise UnknownPackageError if no package found and search by provides returns empty list
    """
    mocker.patch("ahriman.core.alpm.remote.Remote.package_info",
                 side_effect=UnknownPackageError(aur_package_ahriman.name))
    mocker.patch("ahriman.core.alpm.remote.Remote.package_provided_by", return_value=[])

    with pytest.raises(UnknownPackageError):
        Remote.info("ahriman", pacman=pacman, include_provides=True)


def test_multisearch(aur_package_ahriman: AURPackage, pacman: Pacman, mocker: MockerFixture) -> None:
    """
    must search in AUR with multiple words
    """
    terms = ["ahriman", "is", "cool"]
    search_mock = mocker.patch("ahriman.core.alpm.remote.Remote.package_search", return_value=[aur_package_ahriman])

    assert Remote.multisearch(*terms, pacman=pacman, search_by="name") == [aur_package_ahriman]
    search_mock.assert_has_calls([
        MockCall("ahriman", pacman=pacman, search_by="name"),
        MockCall("cool", pacman=pacman, search_by="name"),
    ])


def test_multisearch_empty(pacman: Pacman, mocker: MockerFixture) -> None:
    """
    must return empty list if no long terms supplied
    """
    terms = ["it", "is"]
    search_mock = mocker.patch("ahriman.core.alpm.remote.Remote.package_search")

    assert Remote.multisearch(*terms, pacman=pacman) == []
    search_mock.assert_not_called()


def test_multisearch_single(aur_package_ahriman: AURPackage, pacman: Pacman, mocker: MockerFixture) -> None:
    """
    must search in AUR with one word
    """
    search_mock = mocker.patch("ahriman.core.alpm.remote.Remote.package_search", return_value=[aur_package_ahriman])
    assert Remote.multisearch("ahriman", pacman=pacman) == [aur_package_ahriman]
    search_mock.assert_called_once_with("ahriman", pacman=pacman, search_by=None)


def test_remote_git_url(remote: Remote) -> None:
    """
    must raise NotImplemented for missing remote git url
    """
    with pytest.raises(NotImplementedError):
        remote.remote_git_url("package", "repositories")


def test_remote_web_url(remote: Remote) -> None:
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
    Remote.search("ahriman", pacman=pacman, search_by="name")
    search_mock.assert_called_once_with("ahriman", pacman=pacman, search_by="name")


def test_package_info(remote: Remote, pacman: Pacman) -> None:
    """
    must raise NotImplemented for missing package info method
    """
    with pytest.raises(NotImplementedError):
        remote.package_info("package", pacman=pacman)


def test_package_provided_by(remote: Remote, pacman: Pacman) -> None:
    """
    must return empty list for provides method
    """
    assert remote.package_provided_by("package", pacman=pacman) == []


def test_package_search(remote: Remote, pacman: Pacman) -> None:
    """
    must raise NotImplemented for missing package search method
    """
    with pytest.raises(NotImplementedError):
        remote.package_search("package", pacman=pacman, search_by=None)
