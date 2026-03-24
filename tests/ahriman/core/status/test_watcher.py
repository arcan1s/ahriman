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


async def test_load(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must correctly load packages
    """
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_get",
                              return_value=[(package_ahriman, BuildStatus())])

    await watcher.load()
    cache_mock.assert_called_once_with(None)
    package, status = watcher._known[package_ahriman.base]
    assert package == package_ahriman
    assert status.status == BuildStatusEnum.Unknown


async def test_load_known(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must correctly load packages with known statuses
    """
    status = BuildStatus(BuildStatusEnum.Success)
    mocker.patch("ahriman.core.status.local_client.LocalClient.package_get", return_value=[(package_ahriman, status)])
    watcher._known = {package_ahriman.base: (package_ahriman, status)}

    await watcher.load()
    _, status = watcher._known[package_ahriman.base]
    assert status.status == BuildStatusEnum.Success


async def test_package_archives(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return package archives from package info
    """
    archives_mock = mocker.patch("ahriman.core.repository.package_info.PackageInfo.package_archives",
                                 return_value=[package_ahriman])

    result = await watcher.package_archives(package_ahriman.base)
    assert result == [package_ahriman]
    archives_mock.assert_called_once_with(package_ahriman.base)


async def test_package_get(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must return package status
    """
    watcher._known = {package_ahriman.base: (package_ahriman, BuildStatus())}
    package, status = await watcher.package_get(package_ahriman.base)
    assert package == package_ahriman
    assert status.status == BuildStatusEnum.Unknown


async def test_package_get_failed(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must fail on unknown package
    """
    with pytest.raises(UnknownPackageError):
        await watcher.package_get(package_ahriman.base)


async def test_package_hold_update(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must update package hold status
    """
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_hold_update")
    watcher._known = {package_ahriman.base: (package_ahriman, BuildStatus())}

    await watcher.package_hold_update(package_ahriman.base, enabled=True)
    cache_mock.assert_called_once_with(package_ahriman.base, enabled=True)
    _, status = watcher._known[package_ahriman.base]
    assert status.is_held is True


async def test_package_hold_update_unknown(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must fail on unknown package hold update
    """
    with pytest.raises(UnknownPackageError):
        await watcher.package_hold_update(package_ahriman.base, enabled=True)


async def test_package_remove(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must remove package base
    """
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_remove")
    watcher._known = {package_ahriman.base: (package_ahriman, BuildStatus())}

    await watcher.package_remove(package_ahriman.base)
    assert not watcher._known
    cache_mock.assert_called_once_with(package_ahriman.base)


async def test_package_remove_unknown(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must not fail on unknown base removal
    """
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_remove")
    await watcher.package_remove(package_ahriman.base)
    cache_mock.assert_called_once_with(package_ahriman.base)


async def test_package_status_update(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must update package status only for known package
    """
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_status_update")
    watcher._known = {package_ahriman.base: (package_ahriman, BuildStatus())}

    await watcher.package_status_update(package_ahriman.base, BuildStatusEnum.Success)
    cache_mock.assert_called_once_with(package_ahriman.base, pytest.helpers.anyvar(int))
    package, status = watcher._known[package_ahriman.base]
    assert package == package_ahriman
    assert status.status == BuildStatusEnum.Success


async def test_package_status_update_preserves_hold(watcher: Watcher, package_ahriman: Package,
                                                    mocker: MockerFixture) -> None:
    """
    must preserve hold status on package status update
    """
    mocker.patch("ahriman.core.status.local_client.LocalClient.package_status_update")
    watcher._known = {package_ahriman.base: (package_ahriman, BuildStatus(is_held=True))}

    await watcher.package_status_update(package_ahriman.base, BuildStatusEnum.Success)
    _, status = watcher._known[package_ahriman.base]
    assert status.is_held is True


async def test_package_status_update_unknown(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must fail on unknown package status update only
    """
    with pytest.raises(UnknownPackageError):
        await watcher.package_status_update(package_ahriman.base, BuildStatusEnum.Unknown)


async def test_package_update(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must add package to cache
    """
    cache_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_update")

    await watcher.package_update(package_ahriman, BuildStatusEnum.Unknown)
    assert watcher.packages
    cache_mock.assert_called_once_with(package_ahriman, pytest.helpers.anyvar(int))


async def test_package_update_preserves_hold(watcher: Watcher, package_ahriman: Package,
                                             mocker: MockerFixture) -> None:
    """
    must preserve hold status on package update
    """
    mocker.patch("ahriman.core.status.local_client.LocalClient.package_update")
    watcher._known = {package_ahriman.base: (package_ahriman, BuildStatus(is_held=True))}

    await watcher.package_update(package_ahriman, BuildStatusEnum.Success)
    _, status = watcher._known[package_ahriman.base]
    assert status.is_held is True


async def test_status_update(watcher: Watcher) -> None:
    """
    must update service status
    """
    await watcher.status_update(BuildStatusEnum.Success)
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
