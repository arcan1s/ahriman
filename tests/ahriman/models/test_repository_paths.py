from pytest_mock import MockerFixture
from unittest import mock

from ahriman.models.package import Package
from ahriman.models.repository_paths import RepositoryPaths


def test_known_architectures(repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must list available directory paths
    """
    iterdir_mock = mocker.patch("pathlib.Path.iterdir")
    repository_paths.known_architectures(repository_paths.root)
    iterdir_mock.assert_called_once()


def test_cache_for(repository_paths: RepositoryPaths, package_ahriman: Package) -> None:
    """
    must return correct path for cache directory
    """
    path = repository_paths.cache_for(package_ahriman.base)
    assert path.name == package_ahriman.base
    assert path.parent == repository_paths.cache


def test_manual_for(repository_paths: RepositoryPaths, package_ahriman: Package) -> None:
    """
    must return correct path for manual directory
    """
    path = repository_paths.manual_for(package_ahriman.base)
    assert path.name == package_ahriman.base
    assert path.parent == repository_paths.manual


def test_patches_for(repository_paths: RepositoryPaths, package_ahriman: Package) -> None:
    """
    must return correct path for patches directory
    """
    path = repository_paths.patches_for(package_ahriman.base)
    assert path.name == package_ahriman.base
    assert path.parent == repository_paths.patches


def test_sources_for(repository_paths: RepositoryPaths, package_ahriman: Package) -> None:
    """
    must return correct path for sources directory
    """
    path = repository_paths.sources_for(package_ahriman.base)
    assert path.name == package_ahriman.base
    assert path.parent == repository_paths.sources


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
        and prop not in ("architecture", "known_architectures", "root", "tree_clear", "tree_create")
    }
    mkdir_mock = mocker.patch("pathlib.Path.mkdir")

    repository_paths.tree_create()
    mkdir_mock.assert_has_calls(
        [
            mock.call(mode=0o755, parents=True, exist_ok=True)
            for _ in paths
        ], any_order=True)
