import pytest
import shutil

from pathlib import Path
from pytest_mock import MockerFixture
from unittest import mock

from ahriman.core.build_tools.task import Task


def test_fetch_existing(mocker: MockerFixture) -> None:
    """
    must fetch new package via clone command
    """
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    check_output_mock = mocker.patch("ahriman.core.build_tools.task.Task._check_output")

    local = Path("local")
    Task.fetch(local, "remote", "master")
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
    check_output_mock = mocker.patch("ahriman.core.build_tools.task.Task._check_output")

    local = Path("local")
    Task.fetch(local, "remote", "master")
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


def test_init_with_cache(task_ahriman: Task, mocker: MockerFixture) -> None:
    """
    must copy tree instead of fetch
    """
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("shutil.copytree")
    mocker.patch("ahriman.core.build_tools.task.Task.fetch")

    task_ahriman.init(None)
    shutil.copytree.assert_called_once()
