import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from unittest import mock

from ahriman.core.configuration import Configuration
from ahriman.core.gitremote import RemotePushTrigger
from ahriman.models.package import Package
from ahriman.models.result import Result


def test_package_update(package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must update single package
    """
    rmtree_mock = mocker.patch("shutil.rmtree")
    fetch_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.fetch")
    copytree_mock = mocker.patch("shutil.copytree")

    local = Path("local")
    RemotePushTrigger.package_update(package_ahriman, local)
    rmtree_mock.assert_has_calls([
        mock.call(local / package_ahriman.base, ignore_errors=True),
        mock.call(pytest.helpers.anyvar(int), onerror=pytest.helpers.anyvar(int)),  # removal of the TemporaryDirectory
        mock.call(local / package_ahriman.base / ".git", ignore_errors=True),
    ])
    fetch_mock.assert_called_once_with(pytest.helpers.anyvar(int), package_ahriman.remote)
    copytree_mock.assert_called_once_with(pytest.helpers.anyvar(int), local / package_ahriman.base)


def test_packages_update(result: Result, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must generate packages update
    """
    update_mock = mocker.patch("ahriman.core.gitremote.RemotePushTrigger.package_update",
                               return_value=[package_ahriman.base])

    local = Path("local")
    assert list(RemotePushTrigger.packages_update(result, local))
    update_mock.assert_called_once_with(package_ahriman, local)


def test_on_result(configuration: Configuration, result: Result, package_ahriman: Package,
                   mocker: MockerFixture) -> None:
    """
    must push changes on result
    """
    mocker.patch("ahriman.core.gitremote.RemotePushTrigger.packages_update", return_value=[package_ahriman.base])
    fetch_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.fetch")
    push_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.push")
    trigger = RemotePushTrigger("x86_64", configuration)

    trigger.on_result(result, [package_ahriman])
    fetch_mock.assert_called_once_with(pytest.helpers.anyvar(int), trigger.remote_source)
    push_mock.assert_called_once_with(pytest.helpers.anyvar(int), trigger.remote_source, package_ahriman.base)
