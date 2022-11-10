import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import GitRemoteError
from ahriman.core.gitremote.remote_pull import RemotePull


def test_repo_clone(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must clone repository locally and copy its content
    """
    fetch_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.fetch")
    copy_mock = mocker.patch("ahriman.core.gitremote.remote_pull.RemotePull.repo_copy")
    runner = RemotePull(configuration, "gitremote")

    runner.repo_clone()
    fetch_mock.assert_called_once_with(pytest.helpers.anyvar(int), runner.remote_source)
    copy_mock.assert_called_once_with(pytest.helpers.anyvar(int))


def test_repo_copy(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must copy repository tree from temporary directory to the local cache
    """
    mocker.patch("ahriman.core.gitremote.remote_pull.walk", return_value=[
        Path("local") / "package1" / "PKGBUILD",
        Path("local") / "package1" / ".SRCINFO",
        Path("local") / "package2" / ".SRCINFO",
        Path("local") / "package3" / "PKGBUILD",
        Path("local") / "package3" / ".SRCINFO",
    ])
    copytree_mock = mocker.patch("shutil.copytree")
    init_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.init")
    runner = RemotePull(configuration, "gitremote")

    runner.repo_copy(Path("local"))
    copytree_mock.assert_has_calls([
        MockCall(Path("local") / "package1", configuration.repository_paths.cache_for("package1"), dirs_exist_ok=True),
        MockCall(Path("local") / "package3", configuration.repository_paths.cache_for("package3"), dirs_exist_ok=True),
    ])
    init_mock.assert_has_calls([
        MockCall(configuration.repository_paths.cache_for("package1")),
        MockCall(configuration.repository_paths.cache_for("package3")),
    ])


def test_run(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must clone repo on run
    """
    clone_mock = mocker.patch("ahriman.core.gitremote.remote_pull.RemotePull.repo_clone")
    runner = RemotePull(configuration, "gitremote")

    runner.run()
    clone_mock.assert_called_once_with()


def test_run_failed(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must reraise exception on error occurred
    """
    mocker.patch("ahriman.core.gitremote.remote_pull.RemotePull.repo_clone", side_effect=Exception())
    runner = RemotePull(configuration, "gitremote")

    with pytest.raises(GitRemoteError):
        runner.run()
