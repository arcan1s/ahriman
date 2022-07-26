import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from typing import Callable, Tuple
from unittest import mock
from unittest.mock import MagicMock

from ahriman.core.exceptions import InvalidPath
from ahriman.models.package import Package
from ahriman.models.repository_paths import RepositoryPaths


def _get_owner(root: Path, same: bool) -> Callable[[Path], Tuple[int, int]]:
    """
    mocker function for owner definition

    Args:
        root(Path): root directory
        same(bool): if True then returns the same as root directory and different otherwise

    Returns:
        Callable[[Path], Tuple[int, int]]: function which can define ownership
    """
    root_owner = (42, 42)
    nonroot_owner = (42, 42) if same else (1, 1)
    return lambda path: root_owner if path == root else nonroot_owner


def test_root_owner(repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must correctly define root directory owner
    """
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.owner", return_value=(42, 142))
    assert repository_paths.root_owner == (42, 142)


def test_known_architectures(repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must list available directory paths
    """
    iterdir_mock = mocker.patch("pathlib.Path.iterdir")
    repository_paths.known_architectures(repository_paths.root)
    iterdir_mock.assert_called_once_with()


def test_owner(repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must correctly retrieve owner of the path
    """
    stat_mock = MagicMock()
    stat_mock.st_uid = 42
    stat_mock.st_gid = 142
    mocker.patch("pathlib.Path.stat", return_value=stat_mock)

    assert RepositoryPaths.owner(repository_paths.root) == (42, 142)


def test_cache_for(repository_paths: RepositoryPaths, package_ahriman: Package) -> None:
    """
    must return correct path for cache directory
    """
    path = repository_paths.cache_for(package_ahriman.base)
    assert path.name == package_ahriman.base
    assert path.parent == repository_paths.cache


def test_chown(repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must correctly set owner for the directory
    """
    object.__setattr__(repository_paths, "owner", _get_owner(repository_paths.root, same=False))
    mocker.patch.object(RepositoryPaths, "root_owner", (42, 42))
    chown_mock = mocker.patch("os.chown")

    path = repository_paths.root / "path"
    repository_paths.chown(path)
    chown_mock.assert_called_once_with(path, 42, 42, follow_symlinks=False)


def test_chown_parent(repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must correctly set owner for the directory including parents
    """
    object.__setattr__(repository_paths, "owner", _get_owner(repository_paths.root, same=False))
    mocker.patch.object(RepositoryPaths, "root_owner", (42, 42))
    chown_mock = mocker.patch("os.chown")

    path = repository_paths.root / "parent" / "path"
    repository_paths.chown(path)
    chown_mock.assert_has_calls([
        mock.call(path, 42, 42, follow_symlinks=False),
        mock.call(path.parent, 42, 42, follow_symlinks=False)
    ])


def test_chown_skip(repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must skip ownership set in case if it is same as root
    """
    object.__setattr__(repository_paths, "owner", _get_owner(repository_paths.root, same=True))
    mocker.patch.object(RepositoryPaths, "root_owner", (42, 42))
    chown_mock = mocker.patch("os.chown")

    path = repository_paths.root / "path"
    repository_paths.chown(path)
    chown_mock.assert_not_called()


def test_chown_invalid_path(repository_paths: RepositoryPaths) -> None:
    """
    must raise invalid path exception in case if directory outside the root supplied
    """
    with pytest.raises(InvalidPath):
        repository_paths.chown(repository_paths.root.parent)


def test_tree_clear(repository_paths: RepositoryPaths, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must remove any package related files
    """
    paths = {
        getattr(repository_paths, prop)(package_ahriman.base)
        for prop in dir(repository_paths) if prop.endswith("_for")
    }
    rmtree_mock = mocker.patch("shutil.rmtree")

    repository_paths.tree_clear(package_ahriman.base)
    rmtree_mock.assert_has_calls(
        [
            mock.call(path, ignore_errors=True) for path in paths
        ], any_order=True)


def test_tree_create(repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must create whole tree
    """
    paths = {
        prop
        for prop in dir(repository_paths)
        if not prop.startswith("_")
        and not prop.endswith("_for")
        and prop not in ("architecture",
                         "chown",
                         "known_architectures",
                         "owner",
                         "root",
                         "root_owner",
                         "tree_clear",
                         "tree_create")
    }
    mkdir_mock = mocker.patch("pathlib.Path.mkdir")
    chown_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.chown")

    repository_paths.tree_create()
    mkdir_mock.assert_has_calls(
        [
            mock.call(mode=0o755, parents=True, exist_ok=True)
            for _ in paths
        ], any_order=True)
    chown_mock.assert_has_calls([mock.call(getattr(repository_paths, path)) for path in paths], any_order=True)
