import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from unittest import mock

from ahriman.core.build_tools.sources import Sources


def test_add(mocker: MockerFixture) -> None:
    """
    must add files to git
    """
    glob_mock = mocker.patch("pathlib.Path.glob", return_value=[Path("local/1"), Path("local/2")])
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.Sources._check_output")

    local = Path("local")
    Sources.add(local, "pattern1", "pattern2")
    glob_mock.assert_has_calls([mock.call("pattern1"), mock.call("pattern2")])
    check_output_mock.assert_called_once_with(
        "git", "add", "--intent-to-add", "1", "2", "1", "2",
        exception=None, cwd=local, logger=pytest.helpers.anyvar(int))


def test_add_skip(mocker: MockerFixture) -> None:
    """
    must skip addition of files to index if no fiels found
    """
    mocker.patch("pathlib.Path.glob", return_value=[])
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.Sources._check_output")

    Sources.add(Path("local"), "pattern1")
    check_output_mock.assert_not_called()


def test_diff(mocker: MockerFixture) -> None:
    """
    must calculate diff
    """
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.Sources._check_output")

    local = Path("local")
    assert Sources.diff(local)
    check_output_mock.assert_called_once_with("git", "diff",
                                              exception=None, cwd=local, logger=pytest.helpers.anyvar(int))


def test_fetch_empty(mocker: MockerFixture) -> None:
    """
    must do nothing in case if no branches available
    """
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("ahriman.core.build_tools.sources.Sources.has_remotes", return_value=False)
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.Sources._check_output")

    Sources.fetch(Path("local"), "remote")
    check_output_mock.assert_not_called()


def test_fetch_existing(mocker: MockerFixture) -> None:
    """
    must fetch new package via fetch command
    """
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("ahriman.core.build_tools.sources.Sources.has_remotes", return_value=True)
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.Sources._check_output")

    local = Path("local")
    Sources.fetch(local, "remote")
    check_output_mock.assert_has_calls([
        mock.call("git", "fetch", "origin", Sources._branch,
                  exception=None, cwd=local, logger=pytest.helpers.anyvar(int)),
        mock.call("git", "checkout", "--force", Sources._branch,
                  exception=None, cwd=local, logger=pytest.helpers.anyvar(int)),
        mock.call("git", "reset", "--hard", f"origin/{Sources._branch}",
                  exception=None, cwd=local, logger=pytest.helpers.anyvar(int))
    ])


def test_fetch_new(mocker: MockerFixture) -> None:
    """
    must fetch new package via clone command
    """
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.Sources._check_output")

    local = Path("local")
    Sources.fetch(local, "remote")
    check_output_mock.assert_has_calls([
        mock.call("git", "clone", "remote", str(local), exception=None, logger=pytest.helpers.anyvar(int)),
        mock.call("git", "checkout", "--force", Sources._branch,
                  exception=None, cwd=local, logger=pytest.helpers.anyvar(int)),
        mock.call("git", "reset", "--hard", f"origin/{Sources._branch}",
                  exception=None, cwd=local, logger=pytest.helpers.anyvar(int))
    ])


def test_fetch_new_without_remote(mocker: MockerFixture) -> None:
    """
    must fetch nothing in case if no remote set
    """
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.Sources._check_output")

    local = Path("local")
    Sources.fetch(local, None)
    check_output_mock.assert_has_calls([
        mock.call("git", "checkout", "--force", Sources._branch,
                  exception=None, cwd=local, logger=pytest.helpers.anyvar(int)),
        mock.call("git", "reset", "--hard", f"origin/{Sources._branch}",
                  exception=None, cwd=local, logger=pytest.helpers.anyvar(int))
    ])


def test_has_remotes(mocker: MockerFixture) -> None:
    """
    must ask for remotes
    """
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.Sources._check_output", return_value="origin")

    local = Path("local")
    assert Sources.has_remotes(local)
    check_output_mock.assert_called_once_with("git", "remote",
                                              exception=None, cwd=local, logger=pytest.helpers.anyvar(int))


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
    check_output_mock.assert_called_once_with("git", "init", "--initial-branch", Sources._branch,
                                              exception=None, cwd=local, logger=pytest.helpers.anyvar(int))


def test_load(mocker: MockerFixture) -> None:
    """
    must load packages sources correctly
    """
    fetch_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.fetch")
    patch_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.patch_apply")

    Sources.load(Path("local"), "remote", "patch")
    fetch_mock.assert_called_once_with(Path("local"), "remote")
    patch_mock.assert_called_once_with(Path("local"), "patch")


def test_load_no_patch(mocker: MockerFixture) -> None:
    """
    must load packages sources correctly without patches
    """
    mocker.patch("ahriman.core.build_tools.sources.Sources.fetch")
    patch_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.patch_apply")

    Sources.load(Path("local"), "remote", None)
    patch_mock.assert_not_called()


def test_patch_apply(mocker: MockerFixture) -> None:
    """
    must apply patches if any
    """
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.Sources._check_output")

    local = Path("local")
    Sources.patch_apply(local, "patches")
    check_output_mock.assert_called_once_with(
        "git", "apply", "--ignore-space-change", "--ignore-whitespace",
        exception=None, cwd=local, input_data="patches", logger=pytest.helpers.anyvar(int)
    )


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
