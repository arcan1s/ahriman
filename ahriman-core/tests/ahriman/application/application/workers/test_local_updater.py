from pytest_mock import MockerFixture

from ahriman.application.application.workers.local_updater import LocalUpdater
from ahriman.models.package import Package
from ahriman.models.packagers import Packagers
from ahriman.models.result import Result


def test_partition(local_updater: LocalUpdater, mocker: MockerFixture) -> None:
    """
    must partition as tree resolution
    """
    resolve_mock = mocker.patch("ahriman.core.tree.Tree.resolve")
    local_updater.partition([])
    resolve_mock.assert_called_once_with([])


def test_update(local_updater: LocalUpdater, package_ahriman: Package, result: Result,
                mocker: MockerFixture) -> None:
    """
    must process package updates
    """
    paths = [package.filepath for package in package_ahriman.packages.values()]
    mocker.patch("ahriman.core.repository.Repository.packages_built", return_value=paths)
    build_mock = mocker.patch("ahriman.core.repository.Repository.process_build", return_value=result)
    update_mock = mocker.patch("ahriman.core.repository.Repository.process_update", return_value=result)

    assert local_updater.update([package_ahriman], Packagers("username"), bump_pkgrel=True) == result
    build_mock.assert_called_once_with([package_ahriman], Packagers("username"), bump_pkgrel=True)
    update_mock.assert_called_once_with(paths, Packagers("username"))
