import pytest

from pytest_mock import MockerFixture

from ahriman.core.exceptions import UnknownPackageError
from ahriman.core.status.watcher import Watcher
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.package import Package


def test_packages(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must return list of available packages
    """
    assert not watcher.packages

    watcher._known = {package_ahriman.base: (package_ahriman, BuildStatus())}
    assert watcher.packages


def test_load(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must correctly load packages
    """
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_get",
                              return_value=[(package_ahriman, BuildStatus())])

    watcher.load()
    cache_mock.assert_called_once_with(None)
    package, status = watcher._known[package_ahriman.base]
    assert package == package_ahriman
    assert status.status == BuildStatusEnum.Unknown


def test_load_known(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must correctly load packages with known statuses
    """
    status = BuildStatus(BuildStatusEnum.Success)
    mocker.patch("ahriman.core.status.local_client.LocalClient.package_get", return_value=[(package_ahriman, status)])
    watcher._known = {package_ahriman.base: (package_ahriman, status)}

    watcher.load()
    _, status = watcher._known[package_ahriman.base]
    assert status.status == BuildStatusEnum.Success


def test_package_get(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must return package status
    """
    watcher._known = {package_ahriman.base: (package_ahriman, BuildStatus())}
    package, status = watcher.package_get(package_ahriman.base)
    assert package == package_ahriman
    assert status.status == BuildStatusEnum.Unknown


def test_package_get_failed(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must fail on unknown package
    """
    with pytest.raises(UnknownPackageError):
        watcher.package_get(package_ahriman.base)


def test_package_remove(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must remove package base
    """
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_remove")
    watcher._known = {package_ahriman.base: (package_ahriman, BuildStatus())}

    watcher.package_remove(package_ahriman.base)
    assert not watcher._known
    cache_mock.assert_called_once_with(package_ahriman.base)


def test_package_remove_unknown(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must not fail on unknown base removal
    """
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_remove")
    watcher.package_remove(package_ahriman.base)
    cache_mock.assert_called_once_with(package_ahriman.base)


def test_package_status_update(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must update package status only for known package
    """
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_status_update")
    watcher._known = {package_ahriman.base: (package_ahriman, BuildStatus())}

    watcher.package_status_update(package_ahriman.base, BuildStatusEnum.Success)
    cache_mock.assert_called_once_with(package_ahriman.base, pytest.helpers.anyvar(int))
    package, status = watcher._known[package_ahriman.base]
    assert package == package_ahriman
    assert status.status == BuildStatusEnum.Success


def test_package_status_update_unknown(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must fail on unknown package status update only
    """
    with pytest.raises(UnknownPackageError):
        watcher.package_status_update(package_ahriman.base, BuildStatusEnum.Unknown)


def test_package_update(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must add package to cache
    """
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_update")

    watcher.package_update(package_ahriman, BuildStatusEnum.Unknown)
    assert watcher.packages
    cache_mock.assert_called_once_with(package_ahriman, pytest.helpers.anyvar(int))


def test_status_update(watcher: Watcher) -> None:
    """
    must update service status
    """
    watcher.status_update(BuildStatusEnum.Success)
    assert watcher.status.status == BuildStatusEnum.Success


def test_call(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must return self instance if package exists
    """
    watcher._known = {package_ahriman.base: (package_ahriman, BuildStatus())}
    assert watcher(package_ahriman.base)


def test_call_skip(watcher: Watcher) -> None:
    """
    must return self instance if no package base set
    """
    assert watcher(None)


def test_call_failed(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must raise UnknownPackage
    """
    with pytest.raises(UnknownPackageError):
        assert watcher(package_ahriman.base)


def test_getattr(watcher: Watcher) -> None:
    """
    must return client method call
    """
    assert watcher.package_logs_remove


def test_getattr_unknown_method(watcher: Watcher) -> None:
    """
    must raise AttributeError in case if no reporter attribute found
    """
    with pytest.raises(AttributeError):
        assert watcher.random_method
