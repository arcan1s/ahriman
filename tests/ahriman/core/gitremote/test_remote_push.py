import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.exceptions import GitRemoteError
from ahriman.core.gitremote.remote_push import RemotePush
from ahriman.models.package import Package
from ahriman.models.pkgbuild_patch import PkgbuildPatch
from ahriman.models.result import Result


def test_package_update(database: SQLite, configuration: Configuration, package_ahriman: Package,
                        mocker: MockerFixture) -> None:
    """
    must update single package
    """
    patch1 = PkgbuildPatch(None, "patch")
    patch2 = PkgbuildPatch("key", "value")
    local = Path("local")

    mocker.patch(
        "pathlib.Path.is_file",
        autospec=True,
        side_effect=lambda p: True if p == Path(".gitignore") else False)
    glob_mock = mocker.patch("pathlib.Path.glob", return_value=[Path(".git"), Path(".gitignore")])
    rmtree_mock = mocker.patch("shutil.rmtree")
    unlink_mock = mocker.patch("pathlib.Path.unlink")
    fetch_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.fetch")
    patches_mock = mocker.patch("ahriman.core.database.SQLite.patches_get", return_value=[patch1, patch2])
    patches_write_mock = mocker.patch("ahriman.models.pkgbuild_patch.PkgbuildPatch.write")
    runner = RemotePush(database, configuration, "gitremote")

    assert runner.package_update(package_ahriman, local) == package_ahriman.base
    glob_mock.assert_called_once_with(".git*")
    rmtree_mock.assert_has_calls([
        MockCall(local / package_ahriman.base, ignore_errors=True),
        MockCall(Path(".git")),
    ])
    unlink_mock.assert_called_once_with()
    fetch_mock.assert_called_once_with(pytest.helpers.anyvar(int), package_ahriman.remote)
    patches_mock.assert_called_once_with(package_ahriman.base)
    patches_write_mock.assert_has_calls([
        MockCall(local / package_ahriman.base / f"ahriman-{package_ahriman.base}.patch"),
        MockCall(local / package_ahriman.base / f"ahriman-{patch2.key}.patch"),
    ])


def test_packages_update(database: SQLite, configuration: Configuration, result: Result, package_ahriman: Package,
                         mocker: MockerFixture) -> None:
    """
    must generate packages update
    """
    update_mock = mocker.patch("ahriman.core.gitremote.remote_push.RemotePush.package_update",
                               return_value=[package_ahriman.base])
    runner = RemotePush(database, configuration, "gitremote")

    local = Path("local")
    assert list(runner.packages_update(result, local))
    update_mock.assert_called_once_with(package_ahriman, local)


def test_run(database: SQLite, configuration: Configuration, result: Result, package_ahriman: Package,
             mocker: MockerFixture) -> None:
    """
    must push changes on result
    """
    mocker.patch("ahriman.core.gitremote.remote_push.RemotePush.packages_update", return_value=[package_ahriman.base])
    fetch_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.fetch")
    push_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.push")
    runner = RemotePush(database, configuration, "gitremote")

    runner.run(result)
    fetch_mock.assert_called_once_with(pytest.helpers.anyvar(int), runner.remote_source)
    push_mock.assert_called_once_with(
        pytest.helpers.anyvar(int), runner.remote_source, package_ahriman.base, commit_author=runner.commit_author
    )


def test_run_failed(database: SQLite, configuration: Configuration, result: Result, mocker: MockerFixture) -> None:
    """
    must reraise exception on error occurred
    """
    mocker.patch("ahriman.core.build_tools.sources.Sources.fetch", side_effect=Exception())
    runner = RemotePush(database, configuration, "gitremote")

    with pytest.raises(GitRemoteError):
        runner.run(result)
