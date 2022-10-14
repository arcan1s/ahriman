import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from unittest import mock

from ahriman.core.configuration import Configuration
from ahriman.core.gitremote import RemotePullTrigger


def test_on_start(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must clone repo on start
    """
    clone_mock = mocker.patch("ahriman.core.gitremote.RemotePullTrigger.repo_clone")
    trigger = RemotePullTrigger("x86_64", configuration)

    trigger.on_start()
    clone_mock.assert_called_once_with()


def test_repo_clone(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must clone repository locally and copy its content
    """
    fetch_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.fetch")
    copy_mock = mocker.patch("ahriman.core.gitremote.RemotePullTrigger.repo_copy")
    trigger = RemotePullTrigger("x86_64", configuration)

    trigger.repo_clone()
    fetch_mock.assert_called_once_with(pytest.helpers.anyvar(int), trigger.remote_source)
    copy_mock.assert_called_once_with(pytest.helpers.anyvar(int))


def test_repo_copy(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must copy repository tree from temporary directory to the local cache
    """
    mocker.patch("ahriman.core.gitremote.remote_pull_trigger.walk", return_value=[
        Path("local") / "package1" / "PKGBUILD",
        Path("local") / "package1" / ".SRCINFO",
        Path("local") / "package2" / ".SRCINFO",
        Path("local") / "package3" / "PKGBUILD",
        Path("local") / "package3" / ".SRCINFO",
    ])
    copytree_mock = mocker.patch("shutil.copytree")
    init_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.init")
    trigger = RemotePullTrigger("x86_64", configuration)

    trigger.repo_copy(Path("local"))
    copytree_mock.assert_has_calls([
        mock.call(Path("local") / "package1", configuration.repository_paths.cache_for("package1"), dirs_exist_ok=True),
        mock.call(Path("local") / "package3", configuration.repository_paths.cache_for("package3"), dirs_exist_ok=True),
    ])
    init_mock.assert_has_calls([
        mock.call(configuration.repository_paths.cache_for("package1")),
        mock.call(configuration.repository_paths.cache_for("package3")),
    ])
