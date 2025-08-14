from pytest_mock import MockerFixture

from ahriman.core.archive import ArchiveTrigger
from ahriman.models.package import Package
from ahriman.models.result import Result


def test_on_result(archive_trigger: ArchiveTrigger, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must create symlinks for actual repository
    """
    symlinks_mock = mocker.patch("ahriman.core.archive.archive_tree.ArchiveTree.symlinks_create")
    archive_trigger.on_result(Result(), [package_ahriman])
    symlinks_mock.assert_called_once_with([package_ahriman])


def test_on_start(archive_trigger: ArchiveTrigger, mocker: MockerFixture) -> None:
    """
    must create repository tree on load
    """
    tree_mock = mocker.patch("ahriman.core.archive.archive_tree.ArchiveTree.tree_create")
    archive_trigger.on_start()
    tree_mock.assert_called_once_with()


def test_on_stop(archive_trigger: ArchiveTrigger, mocker: MockerFixture) -> None:
    """
    must create repository tree on load
    """
    symlinks_mock = mocker.patch("ahriman.core.archive.archive_tree.ArchiveTree.symlinks_fix")
    archive_trigger.on_stop()
    symlinks_mock.assert_called_once_with()
