import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from unittest import mock

from ahriman.core.build_tools.sources import Sources
from ahriman.models.package import Package
from ahriman.models.remote_source import RemoteSource
from ahriman.models.repository_paths import RepositoryPaths


def test_extend_architectures(mocker: MockerFixture) -> None:
    """
    must update available architecture list
    """
    mocker.patch("pathlib.Path.is_file", return_value=True)
    archs_mock = mocker.patch("ahriman.models.package.Package.supported_architectures", return_value={"x86_64"})
    write_mock = mocker.patch("ahriman.models.pkgbuild_patch.PkgbuildPatch.write")

    Sources.extend_architectures(Path("local"), "i686")
    archs_mock.assert_called_once_with(Path("local"))
    write_mock.assert_called_once_with(Path("local") / "PKGBUILD")


def test_extend_architectures_skip(mocker: MockerFixture) -> None:
    """
    must skip extending list of the architectures in case if no PKGBUILD file found
    """
    mocker.patch("pathlib.Path.is_file", return_value=False)
    write_mock = mocker.patch("ahriman.models.pkgbuild_patch.PkgbuildPatch.write")

    Sources.extend_architectures(Path("local"), "i686")
    write_mock.assert_not_called()


def test_fetch_empty(remote_source: RemoteSource, mocker: MockerFixture) -> None:
    """
    must do nothing in case if no branches available
    """
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("ahriman.core.build_tools.sources.Sources.has_remotes", return_value=False)
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.Sources._check_output")

    Sources.fetch(Path("local"), remote_source)
    check_output_mock.assert_not_called()


def test_fetch_existing(remote_source: RemoteSource, mocker: MockerFixture) -> None:
    """
    must fetch new package via fetch command
    """
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("ahriman.core.build_tools.sources.Sources.has_remotes", return_value=True)
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.Sources._check_output")
    move_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.move")

    local = Path("local")
    Sources.fetch(local, remote_source)
    check_output_mock.assert_has_calls([
        mock.call("git", "fetch", "origin", remote_source.branch,
                  exception=None, cwd=local, logger=pytest.helpers.anyvar(int)),
        mock.call("git", "checkout", "--force", remote_source.branch,
                  exception=None, cwd=local, logger=pytest.helpers.anyvar(int)),
        mock.call("git", "reset", "--hard", f"origin/{remote_source.branch}",
                  exception=None, cwd=local, logger=pytest.helpers.anyvar(int))
    ])
    move_mock.assert_called_once_with(local.resolve(), local)


def test_fetch_new(remote_source: RemoteSource, mocker: MockerFixture) -> None:
    """
    must fetch new package via clone command
    """
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.Sources._check_output")
    move_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.move")

    local = Path("local")
    Sources.fetch(local, remote_source)
    check_output_mock.assert_has_calls([
        mock.call("git", "clone", "--branch", remote_source.branch, "--single-branch",
                  remote_source.git_url, str(local), exception=None, cwd=local, logger=pytest.helpers.anyvar(int)),
        mock.call("git", "checkout", "--force", remote_source.branch,
                  exception=None, cwd=local, logger=pytest.helpers.anyvar(int)),
        mock.call("git", "reset", "--hard", f"origin/{remote_source.branch}",
                  exception=None, cwd=local, logger=pytest.helpers.anyvar(int))
    ])
    move_mock.assert_called_once_with(local.resolve(), local)


def test_fetch_new_without_remote(mocker: MockerFixture) -> None:
    """
    must fetch nothing in case if no remote set
    """
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.Sources._check_output")
    move_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.move")

    local = Path("local")
    Sources.fetch(local, None)
    check_output_mock.assert_has_calls([
        mock.call("git", "checkout", "--force", Sources.DEFAULT_BRANCH,
                  exception=None, cwd=local, logger=pytest.helpers.anyvar(int)),
        mock.call("git", "reset", "--hard", f"origin/{Sources.DEFAULT_BRANCH}",
                  exception=None, cwd=local, logger=pytest.helpers.anyvar(int))
    ])
    move_mock.assert_called_once_with(local.resolve(), local)


def test_fetch_relative(remote_source: RemoteSource, mocker: MockerFixture) -> None:
    """
    must process move correctly on relative directory
    """
    mocker.patch("ahriman.core.build_tools.sources.Sources._check_output")
    move_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.move")

    Sources.fetch(Path("path"), remote_source)
    move_mock.assert_called_once_with(Path("path").resolve(), Path("path"))


def test_has_remotes(mocker: MockerFixture) -> None:
    """
    must ask for remotes
    """
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.Sources._check_output", return_value="origin")

    local = Path("local")
    assert Sources.has_remotes(local)
    check_output_mock.assert_called_once_with(
        "git", "remote", exception=None, cwd=local, logger=pytest.helpers.anyvar(int))


def test_has_remotes_empty(mocker: MockerFixture) -> None:
    """
    must ask for remotes and return false in case if no remotes found
    """
    mocker.patch("ahriman.core.build_tools.sources.Sources._check_output", return_value="")
    assert not Sources.has_remotes(Path("local"))


def test_init(mocker: MockerFixture) -> None:
    """
    must create empty repository at the specified path
    """
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.Sources._check_output")

    local = Path("local")
    Sources.init(local)
    check_output_mock.assert_called_once_with("git", "init", "--initial-branch", Sources.DEFAULT_BRANCH,
                                              exception=None, cwd=local, logger=pytest.helpers.anyvar(int))


def test_load(package_ahriman: Package, repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must load packages sources correctly
    """
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    fetch_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.fetch")
    patch_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.patch_apply")
    architectures_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.extend_architectures")

    Sources.load(Path("local"), package_ahriman, "patch", repository_paths)
    fetch_mock.assert_called_once_with(Path("local"), package_ahriman.remote)
    patch_mock.assert_called_once_with(Path("local"), "patch")
    architectures_mock.assert_called_once_with(Path("local"), repository_paths.architecture)


def test_load_no_patch(package_ahriman: Package, repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must load packages sources correctly without patches
    """
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    mocker.patch("ahriman.core.build_tools.sources.Sources.fetch")
    patch_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.patch_apply")

    Sources.load(Path("local"), package_ahriman, None, repository_paths)
    patch_mock.assert_not_called()


def test_load_with_cache(package_ahriman: Package, repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must load sources by using local cache
    """
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    copytree_mock = mocker.patch("shutil.copytree")
    mocker.patch("ahriman.core.build_tools.sources.Sources.fetch")

    Sources.load(Path("local"), package_ahriman, None, repository_paths)
    copytree_mock.assert_called_once()  # we do not check full command here, sorry


def test_patch_create(mocker: MockerFixture) -> None:
    """
    must create patch set for the package
    """
    add_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.add")
    diff_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.diff")

    Sources.patch_create(Path("local"), "glob")
    add_mock.assert_called_once_with(Path("local"), "glob")
    diff_mock.assert_called_once_with(Path("local"))


def test_patch_create_with_newline(mocker: MockerFixture) -> None:
    """
    created patch must have new line at the end
    """
    mocker.patch("ahriman.core.build_tools.sources.Sources.add")
    mocker.patch("ahriman.core.build_tools.sources.Sources.diff", return_value="diff")
    assert Sources.patch_create(Path("local"), "glob").endswith("\n")


def test_add(sources: Sources, mocker: MockerFixture) -> None:
    """
    must add files to git
    """
    glob_mock = mocker.patch("pathlib.Path.glob", return_value=[Path("local/1"), Path("local/2")])
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.Sources._check_output")

    local = Path("local")
    sources.add(local, "pattern1", "pattern2")
    glob_mock.assert_has_calls([mock.call("pattern1"), mock.call("pattern2")])
    check_output_mock.assert_called_once_with(
        "git", "add", "--intent-to-add", "1", "2", "1", "2",
        exception=None, cwd=local, logger=pytest.helpers.anyvar(int))


def test_add_skip(sources: Sources, mocker: MockerFixture) -> None:
    """
    must skip addition of files to index if no fiels found
    """
    mocker.patch("pathlib.Path.glob", return_value=[])
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.Sources._check_output")

    sources.add(Path("local"), "pattern1")
    check_output_mock.assert_not_called()


def test_diff(sources: Sources, mocker: MockerFixture) -> None:
    """
    must calculate diff
    """
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.Sources._check_output")

    local = Path("local")
    assert sources.diff(local)
    check_output_mock.assert_called_once_with(
        "git", "diff", exception=None, cwd=local, logger=pytest.helpers.anyvar(int))


def test_move(sources: Sources, mocker: MockerFixture) -> None:
    """
    must move content between directories
    """
    mocker.patch("ahriman.core.build_tools.sources.walk", return_value=[Path("/source/path")])
    move_mock = mocker.patch("shutil.move")

    sources.move(Path("/source"), Path("/destination"))
    move_mock.assert_called_once_with(Path("/source/path"), Path("/destination/path"))


def test_move_same(sources: Sources, mocker: MockerFixture) -> None:
    """
    must not do anything in case if directories are the same
    """
    walk_mock = mocker.patch("ahriman.core.build_tools.sources.walk")
    sources.move(Path("/same"), Path("/same"))
    walk_mock.assert_not_called()


def test_patch_apply(sources: Sources, mocker: MockerFixture) -> None:
    """
    must apply patches if any
    """
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.Sources._check_output")

    local = Path("local")
    sources.patch_apply(local, "patches")
    check_output_mock.assert_called_once_with(
        "git", "apply", "--ignore-space-change", "--ignore-whitespace",
        exception=None, cwd=local, input_data="patches", logger=pytest.helpers.anyvar(int)
    )
