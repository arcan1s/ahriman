import pytest
import tempfile

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import PropertyMock

from ahriman.core.exceptions import UnknownPackage
from ahriman.core.status.watcher import Watcher
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.package import Package


def test_cache_load(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must load state from cache
    """
    response = {"packages": [pytest.helpers.get_package_status_extended(package_ahriman)]}

    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("pathlib.Path.open")
    mocker.patch("json.load", return_value=response)

    watcher.known = {package_ahriman.base: (None, None)}
    watcher._cache_load()

    package, status = watcher.known[package_ahriman.base]
    assert package == package_ahriman
    assert status.status == BuildStatusEnum.Unknown


def test_cache_load_json_error(watcher: Watcher, mocker: MockerFixture) -> None:
    """
    must not fail on json errors
    """
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("pathlib.Path.open")
    mocker.patch("json.load", side_effect=Exception())

    watcher._cache_load()
    assert not watcher.known


def test_cache_load_no_file(watcher: Watcher, mocker: MockerFixture) -> None:
    """
    must not fail on missing file
    """
    mocker.patch("pathlib.Path.is_file", return_value=False)

    watcher._cache_load()
    assert not watcher.known


def test_cache_load_unknown(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must not load unknown package
    """
    response = {"packages": [pytest.helpers.get_package_status_extended(package_ahriman)]}

    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("pathlib.Path.open")
    mocker.patch("json.load", return_value=response)

    watcher._cache_load()
    assert not watcher.known


def test_cache_save(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must save state to cache
    """
    mocker.patch("pathlib.Path.open")
    json_mock = mocker.patch("json.dump")

    watcher.known = {package_ahriman.base: (package_ahriman, BuildStatus())}
    watcher._cache_save()
    json_mock.assert_called_once()


def test_cache_save_failed(watcher: Watcher, mocker: MockerFixture) -> None:
    """
    must not fail on dumping packages
    """
    mocker.patch("pathlib.Path.open")
    mocker.patch("json.dump", side_effect=Exception())

    watcher._cache_save()


def test_cache_save_load(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must save state to cache which can be loaded later
    """
    dump_file = Path(tempfile.mktemp())
    mocker.patch("ahriman.core.status.watcher.Watcher.cache_path",
                 new_callable=PropertyMock, return_value=dump_file)
    known_current = {package_ahriman.base: (package_ahriman, BuildStatus())}

    watcher.known = known_current
    watcher._cache_save()

    watcher.known = {package_ahriman.base: (None, None)}
    watcher._cache_load()
    assert watcher.known == known_current

    dump_file.unlink()


def test_get(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must return package status
    """
    watcher.known = {package_ahriman.base: (package_ahriman, BuildStatus())}
    package, status = watcher.get(package_ahriman.base)
    assert package == package_ahriman
    assert status.status == BuildStatusEnum.Unknown


def test_get_failed(watcher: Watcher, package_ahriman: Package) -> None:
    """
    must fail on unknown package
    """
    with pytest.raises(UnknownPackage):
        watcher.get(package_ahriman.base)


def test_load(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must correctly load packages
    """
    mocker.patch("ahriman.core.repository.repository.Repository.packages", return_value=[package_ahriman])
    cache_mock = mocker.patch("ahriman.core.status.watcher.Watcher._cache_load")

    watcher.load()
    cache_mock.assert_called_once()
    package, status = watcher.known[package_ahriman.base]
    assert package == package_ahriman
    assert status.status == BuildStatusEnum.Unknown


def test_load_known(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must correctly load packages with known statuses
    """
    mocker.patch("ahriman.core.repository.repository.Repository.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.core.status.watcher.Watcher._cache_load")
    watcher.known = {package_ahriman.base: (package_ahriman, BuildStatus(BuildStatusEnum.Success))}

    watcher.load()
    _, status = watcher.known[package_ahriman.base]
    assert status.status == BuildStatusEnum.Success


def test_remove(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must remove package base
    """
    cache_mock = mocker.patch("ahriman.core.status.watcher.Watcher._cache_save")
    watcher.known = {package_ahriman.base: (package_ahriman, BuildStatus())}

    watcher.remove(package_ahriman.base)
    assert not watcher.known
    cache_mock.assert_called_once()


def test_remove_unknown(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must not fail on unknown base removal
    """
    cache_mock = mocker.patch("ahriman.core.status.watcher.Watcher._cache_save")

    watcher.remove(package_ahriman.base)
    cache_mock.assert_called_once()


def test_update(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must update package status
    """
    cache_mock = mocker.patch("ahriman.core.status.watcher.Watcher._cache_save")

    watcher.update(package_ahriman.base, BuildStatusEnum.Unknown, package_ahriman)
    cache_mock.assert_called_once()
    package, status = watcher.known[package_ahriman.base]
    assert package == package_ahriman
    assert status.status == BuildStatusEnum.Unknown


def test_update_ping(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must update package status only for known package
    """
    cache_mock = mocker.patch("ahriman.core.status.watcher.Watcher._cache_save")
    watcher.known = {package_ahriman.base: (package_ahriman, BuildStatus())}

    watcher.update(package_ahriman.base, BuildStatusEnum.Success, None)
    cache_mock.assert_called_once()
    package, status = watcher.known[package_ahriman.base]
    assert package == package_ahriman
    assert status.status == BuildStatusEnum.Success


def test_update_unknown(watcher: Watcher, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must fail on unknown package status update only
    """
    cache_mock = mocker.patch("ahriman.core.status.watcher.Watcher._cache_save")

    with pytest.raises(UnknownPackage):
        watcher.update(package_ahriman.base, BuildStatusEnum.Unknown, None)
        cache_mock.assert_called_once()


def test_update_self(watcher: Watcher) -> None:
    """
    must update service status
    """
    watcher.update_self(BuildStatusEnum.Success)
    assert watcher.status.status == BuildStatusEnum.Success
