import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import GitRemoteError
from ahriman.core.gitremote.remote_pull import RemotePull
from ahriman.models.package import Package


def test_repo_clone(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must clone repository locally and copy its content
    """
    fetch_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.fetch")
    copy_mock = mocker.patch("ahriman.core.gitremote.remote_pull.RemotePull.repo_copy")
    _, repository_id = configuration.check_loaded()
    runner = RemotePull(repository_id, configuration, "gitremote")

    runner.repo_clone()
    fetch_mock.assert_called_once_with(pytest.helpers.anyvar(int), runner.remote_source)
    copy_mock.assert_called_once_with(pytest.helpers.anyvar(int))


def test_package_copy(configuration: Configuration, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must copy single package
    """
    package_mock = mocker.patch("ahriman.models.package.Package.from_build", return_value=package_ahriman)
    patterns = object()
    ignore_patterns_mock = mocker.patch("shutil.ignore_patterns", return_value=patterns)
    copytree_mock = mocker.patch("shutil.copytree")
    init_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.init")
    _, repository_id = configuration.check_loaded()
    runner = RemotePull(repository_id, configuration, "gitremote")
    local = Path("local")

    runner.package_copy(local / "PKGBUILD")
    package_mock.assert_called_once_with(local, "x86_64", None)
    ignore_patterns_mock.assert_called_once_with(".git*")
    copytree_mock.assert_called_once_with(
        local, configuration.repository_paths.cache_for(package_ahriman.base),
        ignore=patterns, dirs_exist_ok=True)
    init_mock.assert_called_once_with(configuration.repository_paths.cache_for(package_ahriman.base))


def test_repo_copy(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must copy repository tree from temporary directory to the local cache
    """
    local = Path("local")
    mocker.patch("ahriman.core.gitremote.remote_pull.walk", return_value=[
        local / "package1" / "PKGBUILD",
        local / "package1" / ".SRCINFO",
        local / "package2" / ".SRCINFO",
        local / "package3" / "PKGBUILD",
        local / "package3" / ".SRCINFO",
    ])
    copy_mock = mocker.patch("ahriman.core.gitremote.remote_pull.RemotePull.package_copy")
    _, repository_id = configuration.check_loaded()
    runner = RemotePull(repository_id, configuration, "gitremote")

    runner.repo_copy(local)
    copy_mock.assert_has_calls([
        MockCall(local / "package1" / "PKGBUILD"),
        MockCall(local / "package3" / "PKGBUILD"),
    ])


def test_run(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must clone repo on run
    """
    clone_mock = mocker.patch("ahriman.core.gitremote.remote_pull.RemotePull.repo_clone")
    _, repository_id = configuration.check_loaded()
    runner = RemotePull(repository_id, configuration, "gitremote")

    runner.run()
    clone_mock.assert_called_once_with()


def test_run_failed(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must reraise exception on error occurred
    """
    mocker.patch("ahriman.core.gitremote.remote_pull.RemotePull.repo_clone", side_effect=Exception())
    _, repository_id = configuration.check_loaded()
    runner = RemotePull(repository_id, configuration, "gitremote")

    with pytest.raises(GitRemoteError):
        runner.run()
