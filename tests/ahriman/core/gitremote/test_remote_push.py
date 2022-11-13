import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import GitRemoteError
from ahriman.core.gitremote.remote_push import RemotePush
from ahriman.models.package import Package
from ahriman.models.result import Result


def test_package_update(package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must update single package
    """
    rmtree_mock = mocker.patch("shutil.rmtree")
    fetch_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.fetch")

    local = Path("local")
    RemotePush.package_update(package_ahriman, local)
    rmtree_mock.assert_has_calls([
        MockCall(local / package_ahriman.base, ignore_errors=True),
        MockCall(local / package_ahriman.base / ".git", ignore_errors=True),
    ])
    fetch_mock.assert_called_once_with(pytest.helpers.anyvar(int), package_ahriman.remote)


def test_packages_update(result: Result, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must generate packages update
    """
    update_mock = mocker.patch("ahriman.core.gitremote.remote_push.RemotePush.package_update",
                               return_value=[package_ahriman.base])

    local = Path("local")
    assert list(RemotePush.packages_update(result, local))
    update_mock.assert_called_once_with(package_ahriman, local)


def test_run(configuration: Configuration, result: Result, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must push changes on result
    """
    mocker.patch("ahriman.core.gitremote.remote_push.RemotePush.packages_update", return_value=[package_ahriman.base])
    fetch_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.fetch")
    push_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.push")
    runner = RemotePush(configuration, "gitremote")

    runner.run(result)
    fetch_mock.assert_called_once_with(pytest.helpers.anyvar(int), runner.remote_source)
    push_mock.assert_called_once_with(
        pytest.helpers.anyvar(int), runner.remote_source, package_ahriman.base, commit_author=runner.commit_author
    )


def test_run_failed(configuration: Configuration, result: Result, mocker: MockerFixture) -> None:
    """
    must reraise exception on error occurred
    """
    mocker.patch("ahriman.core.build_tools.sources.Sources.fetch", side_effect=Exception())
    runner = RemotePush(configuration, "gitremote")

    with pytest.raises(GitRemoteError):
        runner.run(result)
