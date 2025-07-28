import pytest

from collections.abc import Callable
from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.models.package import Package
from ahriman.models.repository_id import RepositoryId
from ahriman.models.repository_paths import RepositoryPaths


def _get_owner(root: Path, same: bool) -> Callable[[Path], tuple[int, int]]:
    """
    mocker function for owner definition

    Args:
        root(Path): root directory
        same(bool): if True then returns the same as root directory and different otherwise

    Returns:
        Callable[[Path], tuple[int, int]]: function which can define ownership
    """
    root_owner = (42, 42)
    non_root_owner = (42, 42) if same else (1, 1)
    return lambda path: root_owner if path == root else non_root_owner


def test_suffix(repository_id: RepositoryId, mocker: MockerFixture) -> None:
    """
    must correctly define suffix
    """
    is_dir_mock = mocker.patch("pathlib.Path.is_dir", autospec=True)

    is_dir_mock.return_value = True
    instance = RepositoryPaths(Path("root"), repository_id)
    assert instance._suffix == Path(repository_id.architecture)

    is_dir_mock.return_value = False
    instance = RepositoryPaths(Path("root"), repository_id)
    assert instance._suffix == Path(repository_id.name) / repository_id.architecture

    is_dir_mock.return_value = True
    instance = RepositoryPaths(Path("root"), repository_id, _force_current_tree=True)
    assert instance._suffix == Path(repository_id.name) / repository_id.architecture

    is_dir_mock.assert_has_calls([
        MockCall(Path("root") / "repository" / repository_id.architecture),
        MockCall(Path("root") / "repository" / repository_id.architecture),
    ])


def test_root_owner(repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must correctly define root directory owner
    """
    mocker.patch("ahriman.models.repository_paths.owner", return_value=(42, 142))
    assert repository_paths.root_owner == (42, 142)


def test_known_architectures(repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must list available directory paths /repository/repo/arch
    """
    is_dir_mock = mocker.patch("pathlib.Path.is_dir", autospec=True, return_value=True)
    iterdir_mock = mocker.patch("pathlib.Path.iterdir", autospec=True, return_value=[Path("i686"), Path("x86_64")])

    assert repository_paths.known_architectures(repository_paths.root, repository_paths.repository_id.name) == {
        "i686",
        "x86_64",
    }
    iterdir_mock.assert_called_once_with(repository_paths._repository_root / repository_paths.repository_id.name)
    is_dir_mock.assert_has_calls([
        MockCall(repository_paths._repository_root / repository_paths.repository_id.name),
        MockCall(Path("i686")),
        MockCall(Path("x86_64")),
    ])


def test_known_architectures_legacy(repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must list available directory paths /repository/arch
    """
    def is_dir(path: Path) -> bool:
        return path.name != repository_paths.repository_id.name

    is_dir_mock = mocker.patch("pathlib.Path.is_dir", autospec=True, side_effect=is_dir)
    iterdir_mock = mocker.patch("pathlib.Path.iterdir", autospec=True, return_value=[Path("i686"), Path("x86_64")])

    assert repository_paths.known_architectures(repository_paths.root, repository_paths.repository_id.name) == {
        "i686",
        "x86_64",
    }
    iterdir_mock.assert_called_once_with(repository_paths._repository_root)
    is_dir_mock.assert_has_calls([
        MockCall(repository_paths._repository_root / repository_paths.repository_id.name),
        MockCall(repository_paths._repository_root),
        MockCall(Path("i686")),
        MockCall(Path("x86_64")),
    ])


def test_known_architectures_legacy_backward(repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must list available directory paths /repository/arch in backward compatibility mode
    """
    def is_dir(path: Path) -> bool:
        return path.name != repository_paths.repository_id.name

    is_dir_mock = mocker.patch("pathlib.Path.is_dir", autospec=True, side_effect=is_dir)
    iterdir_mock = mocker.patch("pathlib.Path.iterdir", autospec=True, return_value=[Path("i686"), Path("x86_64")])

    assert repository_paths.known_architectures(repository_paths.root) == {"i686", "x86_64"}
    iterdir_mock.assert_called_once_with(repository_paths._repository_root)
    is_dir_mock.assert_has_calls([
        MockCall(repository_paths._repository_root),
        MockCall(Path("i686")),
        MockCall(Path("x86_64")),
    ])


def test_known_architectures_empty(repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must return empty architectures if tree is not available
    """
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    iterdir_mock = mocker.patch("pathlib.Path.iterdir")

    # new style
    assert not repository_paths.known_architectures(repository_paths.root, repository_paths.repository_id.name)
    # legacy mode
    assert not repository_paths.known_architectures(repository_paths.root)
    iterdir_mock.assert_not_called()


def test_known_repositories(repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must list available directory paths /repository/repo
    """
    def iterdir(path: Path) -> list[Path]:
        if path == repository_paths._repository_root:
            return [Path("repo1"), Path("repo2")]
        return [Path("x86_64")]

    is_dir_mock = mocker.patch("pathlib.Path.is_dir", autospec=True, return_value=True)
    iterdir_mock = mocker.patch("pathlib.Path.iterdir", autospec=True, side_effect=iterdir)

    assert repository_paths.known_repositories(repository_paths.root) == {"repo1", "repo2"}
    iterdir_mock.assert_has_calls([
        MockCall(repository_paths._repository_root),
        MockCall(Path("repo1")),
        MockCall(Path("repo2")),
    ])
    is_dir_mock.assert_has_calls([
        MockCall(repository_paths._repository_root),
        MockCall(Path("repo1")),
        MockCall(Path("x86_64")),
        MockCall(Path("repo2")),
        MockCall(Path("x86_64")),
    ])


def test_known_repositories_legacy(repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must return empty repository list for legacy tree
    """
    def is_dir(path: Path) -> bool:
        return path == repository_paths._repository_root

    mocker.patch("pathlib.Path.is_dir", autospec=True, side_effect=is_dir)
    iterdir_mock = mocker.patch("pathlib.Path.iterdir", autospec=True, return_value=[Path("i686"), Path("x86_64")])

    assert not repository_paths.known_repositories(repository_paths.root)
    iterdir_mock.assert_called_once_with(repository_paths._repository_root)


def test_known_repositories_empty(repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must return empty repositories if tree is not available
    """
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    iterdir_mock = mocker.patch("pathlib.Path.iterdir")

    assert not repository_paths.known_repositories(repository_paths.root)
    iterdir_mock.assert_not_called()


def test_archive_for(repository_paths: RepositoryPaths, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must correctly define archive path
    """
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    path = repository_paths.archive_for(package_ahriman.base)
    assert path == repository_paths.archive / "packages" / "a" / package_ahriman.base


def test_archive_for_create_tree(repository_paths: RepositoryPaths, package_ahriman: Package,
                                 mocker: MockerFixture) -> None:
    """
    must create archive directory if it doesn't exist
    """
    owner_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.preserve_owner")
    mkdir_mock = mocker.patch("pathlib.Path.mkdir")

    repository_paths.archive_for(package_ahriman.base)
    owner_mock.assert_called_once_with(repository_paths.archive)
    mkdir_mock.assert_called_once_with(mode=0o755, parents=True)


def test_cache_for(repository_paths: RepositoryPaths, package_ahriman: Package) -> None:
    """
    must return correct path for cache directory
    """
    path = repository_paths.cache_for(package_ahriman.base)
    assert path.name == package_ahriman.base
    assert path.parent == repository_paths.cache


def test_preserve_owner(tmp_path: Path, repository_id: RepositoryId, mocker: MockerFixture) -> None:
    """
    must preserve file owner during operations
    """
    mocker.patch("os.geteuid", return_value=0)
    mocker.patch("os.getegid", return_value=0)
    seteuid_mock = mocker.patch("os.seteuid")
    setegid_mock = mocker.patch("os.setegid")

    repository_paths = RepositoryPaths(tmp_path, repository_id)
    target_uid, target_gid = repository_paths.root_owner
    repository_paths.tree_create()
    seteuid_mock.assert_has_calls([MockCall(target_uid), MockCall(0)])
    setegid_mock.assert_has_calls([MockCall(target_gid), MockCall(0)])


def test_preserve_owner_exception(tmp_path: Path, repository_id: RepositoryId, mocker: MockerFixture) -> None:
    """
    must return to original uid and gid even during exception
    """
    mocker.patch("os.geteuid", return_value=0)
    mocker.patch("os.getegid", return_value=0)
    mocker.patch("pathlib.Path.mkdir", side_effect=Exception)
    seteuid_mock = mocker.patch("os.seteuid")
    setegid_mock = mocker.patch("os.setegid")

    repository_paths = RepositoryPaths(tmp_path, repository_id)
    target_uid, target_gid = repository_paths.root_owner
    with pytest.raises(Exception):
        repository_paths.tree_create()
    seteuid_mock.assert_has_calls([MockCall(target_uid), MockCall(0)])
    setegid_mock.assert_has_calls([MockCall(target_gid), MockCall(0)])


def test_preserve_owner_non_root(tmp_path: Path, repository_id: RepositoryId, mocker: MockerFixture) -> None:
    """
    must skip processing if user is not root
    """
    mocker.patch("os.geteuid", return_value=42)
    mocker.patch("os.getegid", return_value=42)
    repository_paths = RepositoryPaths(tmp_path, repository_id)
    seteuid_mock = mocker.patch("os.seteuid")
    setegid_mock = mocker.patch("os.setegid")

    repository_paths.tree_create()
    seteuid_mock.assert_not_called()
    setegid_mock.assert_not_called()


def test_preserve_owner_no_directory(tmp_path: Path, repository_id: RepositoryId, mocker: MockerFixture) -> None:
    """
    must skip directory scan if it does not exist
    """
    repository_paths = RepositoryPaths(tmp_path, repository_id)
    chown_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths._chown")

    with repository_paths.preserve_owner(Path("empty")):
        (repository_paths.root / "created1").touch()
    chown_mock.assert_not_called()


def test_tree_clear(repository_paths: RepositoryPaths, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must remove any package related files
    """
    paths = {
        repository_paths.cache_for(package_ahriman.base),
    }
    rmtree_mock = mocker.patch("shutil.rmtree")

    repository_paths.tree_clear(package_ahriman.base)
    rmtree_mock.assert_has_calls(
        [
            MockCall(path, ignore_errors=True) for path in paths
        ], any_order=True)


def test_tree_create(repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must create whole tree
    """
    paths = {
        prop
        for prop in dir(repository_paths)
        if not prop.startswith("_")
        and prop not in (
            "archive_for",
            "build_root",
            "logger_name",
            "logger",
            "repository_id",
            "root",
            "root_owner",
        )
        and not callable(getattr(repository_paths, prop))
    }
    mkdir_mock = mocker.patch("pathlib.Path.mkdir")
    owner_guard_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.preserve_owner")

    repository_paths.tree_create()
    mkdir_mock.assert_has_calls([MockCall(mode=0o755, parents=True, exist_ok=True) for _ in paths], any_order=True)
    owner_guard_mock.assert_called_once_with()


def test_tree_create_skip(mocker: MockerFixture) -> None:
    """
    must skip tree creation if repository id is not set
    """
    mkdir_mock = mocker.patch("pathlib.Path.mkdir")
    repository_paths = RepositoryPaths(Path("local"), RepositoryId("", ""))

    repository_paths.tree_create()
    mkdir_mock.assert_not_called()
