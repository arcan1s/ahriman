from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.core.archive.archive_tree import ArchiveTree
from ahriman.core.utils import utcnow
from ahriman.models.package import Package


def test_repository_for(archive_tree: ArchiveTree) -> None:
    """
    must correctly generate path to repository
    """
    path = archive_tree.repository_for()
    assert path.is_relative_to(archive_tree.paths.archive / "repos")
    assert (archive_tree.repository_id.name, archive_tree.repository_id.architecture) == path.parts[-2:]
    assert set(map("{:02d}".format, utcnow().timetuple()[:3])).issubset(path.parts)


def test_symlinks_create(archive_tree: ArchiveTree, package_ahriman: Package, package_python_schedule: Package,
                         mocker: MockerFixture) -> None:
    """
    must create symlinks
    """
    _original_exists = Path.exists

    symlinks_mock = mocker.patch("pathlib.Path.symlink_to", side_effect=(None, FileExistsError, FileExistsError))
    add_mock = mocker.patch("ahriman.core.alpm.repo.Repo.add")
    mocker.patch("pathlib.Path.glob", autospec=True, side_effect=lambda path, name: [path / name[:-1]])

    archive_tree.symlinks_create([package_ahriman, package_python_schedule])
    symlinks_mock.assert_has_calls([
        MockCall(Path("..") /
                 ".." /
                 ".." /
                 ".." /
                 ".." /
                 ".." /
                 archive_tree.paths.archive_for(package.base)
                 .relative_to(archive_tree.paths.root)
                 .relative_to("archive") /
                 single.filename
        )
        for package in (package_ahriman, package_python_schedule)
        for single in package.packages.values()
    ])
    add_mock.assert_called_once_with(
        archive_tree.repository_for() / package_ahriman.packages[package_ahriman.base].filename
    )


def test_symlinks_create_empty_filename(archive_tree: ArchiveTree, package_ahriman: Package,
                                        mocker: MockerFixture) -> None:
    """
    must skip symlinks creation if filename is not set
    """
    package_ahriman.packages[package_ahriman.base].filename = None
    symlinks_mock = mocker.patch("pathlib.Path.symlink_to")

    archive_tree.symlinks_create([package_ahriman])
    symlinks_mock.assert_not_called()


def test_symlinks_fix(archive_tree: ArchiveTree, mocker: MockerFixture) -> None:
    """
    must fix broken symlinks
    """
    _original_exists = Path.exists

    def exists_mock(path: Path) -> bool:
        if path.name == "symlink":
            return True
        return _original_exists(path)

    mocker.patch("pathlib.Path.is_symlink", side_effect=[True, True, False])
    mocker.patch("pathlib.Path.exists", autospec=True, side_effect=exists_mock)
    walk_mock = mocker.patch("ahriman.core.archive.archive_tree.walk", return_value=[
        archive_tree.repository_for() / filename
        for filename in ("symlink", "broken_symlink", "file")
    ])
    remove_mock = mocker.patch("ahriman.core.alpm.repo.Repo.remove")

    archive_tree.symlinks_fix()
    walk_mock.assert_called_once_with(archive_tree.paths.archive / "repos")
    remove_mock.assert_called_once_with(None, archive_tree.repository_for() / "broken_symlink")


def test_symlinks_fix_foreign_repository(archive_tree: ArchiveTree, mocker: MockerFixture) -> None:
    """
    must skip symlinks check if repository name or architecture doesn't match
    """
    _original_exists = Path.exists

    def exists_mock(path: Path) -> bool:
        if path.name == "symlink":
            return True
        return _original_exists(path)

    mocker.patch("pathlib.Path.is_symlink", side_effect=[True, True, False])
    mocker.patch("pathlib.Path.exists", autospec=True, side_effect=exists_mock)
    mocker.patch("ahriman.core.archive.archive_tree.walk", return_value=[
        archive_tree.repository_for().with_name("i686") / filename
        for filename in ("symlink", "broken_symlink", "file")
    ])
    remove_mock = mocker.patch("ahriman.core.alpm.repo.Repo.remove")

    archive_tree.symlinks_fix()
    remove_mock.assert_not_called()


def test_tree_create(archive_tree: ArchiveTree, mocker: MockerFixture) -> None:
    """
    must create repository root if not exists
    """
    owner_guard_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.preserve_owner")
    mkdir_mock = mocker.patch("pathlib.Path.mkdir")
    init_mock = mocker.patch("ahriman.core.alpm.repo.Repo.init")

    archive_tree.tree_create()
    owner_guard_mock.assert_called_once_with(archive_tree.paths.archive)
    mkdir_mock.assert_called_once_with(0o755, parents=True)
    init_mock.assert_called_once_with()


def test_tree_create_exists(archive_tree: ArchiveTree, mocker: MockerFixture) -> None:
    """
    must skip directory creation if already exists
    """
    mocker.patch("pathlib.Path.exists", return_value=True)
    mkdir_mock = mocker.patch("pathlib.Path.mkdir")

    archive_tree.tree_create()
    mkdir_mock.assert_not_called()
