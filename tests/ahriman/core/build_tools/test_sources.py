import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from unittest import mock

from ahriman.core.build_tools.sources import Sources


def test_fetch_existing(mocker: MockerFixture) -> None:
    """
    must fetch new package via clone command
    """
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.Sources._check_output")

    local = Path("local")
    Sources.fetch(local, "remote", "master")
    check_output_mock.assert_has_calls([
        mock.call("git", "fetch", "origin", "master",
                  exception=pytest.helpers.anyvar(int),
                  cwd=local, logger=pytest.helpers.anyvar(int)),
        mock.call("git", "checkout", "--force", "master",
                  exception=pytest.helpers.anyvar(int),
                  cwd=local, logger=pytest.helpers.anyvar(int)),
        mock.call("git", "reset", "--hard", "origin/master",
                  exception=pytest.helpers.anyvar(int),
                  cwd=local, logger=pytest.helpers.anyvar(int))
    ])


def test_fetch_new(mocker: MockerFixture) -> None:
    """
    must fetch new package via clone command
    """
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.Sources._check_output")

    local = Path("local")
    Sources.fetch(local, "remote", "master")
    check_output_mock.assert_has_calls([
        mock.call("git", "clone", "remote", str(local),
                  exception=pytest.helpers.anyvar(int),
                  logger=pytest.helpers.anyvar(int)),
        mock.call("git", "checkout", "--force", "master",
                  exception=pytest.helpers.anyvar(int),
                  cwd=local, logger=pytest.helpers.anyvar(int)),
        mock.call("git", "reset", "--hard", "origin/master",
                  exception=pytest.helpers.anyvar(int),
                  cwd=local, logger=pytest.helpers.anyvar(int))
    ])


def test_load(mocker: MockerFixture) -> None:
    """
    must load packages sources correctly
    """
    fetch_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.fetch")
    patch_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.patch")

    Sources.load(Path("local"), "remote", Path("patches"))
    fetch_mock.assert_called_with(Path("local"), "remote")
    patch_mock.assert_called_with(Path("local"), Path("patches"))


def test_patches(mocker: MockerFixture) -> None:
    """
    must apply patches if any
    """
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    glob_mock = mocker.patch("pathlib.Path.glob", return_value=[Path("01.patch"), Path("02.patch")])
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.Sources._check_output")

    local = Path("local")
    Sources.patch(local, Path("patches"))
    glob_mock.assert_called_once()
    check_output_mock.assert_has_calls([
        mock.call("git", "apply", "--ignore-space-change", "--ignore-whitespace", "01.patch",
                  exception=pytest.helpers.anyvar(int),
                  cwd=local, logger=pytest.helpers.anyvar(int)),
        mock.call("git", "apply", "--ignore-space-change", "--ignore-whitespace", "02.patch",
                  exception=pytest.helpers.anyvar(int),
                  cwd=local, logger=pytest.helpers.anyvar(int)),
    ])


def test_patches_no_dir(mocker: MockerFixture) -> None:
    """
    must not fail if no patches directory exists
    """
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    glob_mock = mocker.patch("pathlib.Path.glob")

    Sources.patch(Path("local"), Path("patches"))
    glob_mock.assert_not_called()


def test_patches_no_patches(mocker: MockerFixture) -> None:
    """
    must not fail if no patches exist
    """
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("pathlib.Path.glob", return_value=[])
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.Sources._check_output")

    Sources.patch(Path("local"), Path("patches"))
    check_output_mock.assert_not_called()
