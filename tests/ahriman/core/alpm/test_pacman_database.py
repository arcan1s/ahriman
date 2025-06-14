import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import MagicMock, call as MockCall

from ahriman.core.alpm.pacman_database import PacmanDatabase
from ahriman.core.exceptions import PacmanError


def test_copy(mocker: MockerFixture) -> None:
    """
    must copy local database file
    """
    copy_mock = mocker.patch("shutil.copy")
    PacmanDatabase.copy(Path("remote"), Path("local"))
    copy_mock.assert_called_once_with(Path("remote"), Path("local"))


def test_download(pacman_database: PacmanDatabase, mocker: MockerFixture) -> None:
    """
    must download database by remote url
    """
    response_obj = MagicMock()
    response_obj.headers = {pacman_database.LAST_MODIFIED_HEADER: "Fri, 09 Feb 2024 00:25:55 GMT"}
    response_obj.iter_content.return_value = ["chunk".encode("utf8")]

    path = Path("local")
    url = "url"

    file_mock = MagicMock()
    request_mock = mocker.patch("ahriman.core.alpm.pacman_database.PacmanDatabase.make_request",
                                return_value=response_obj)
    open_mock = mocker.patch("pathlib.Path.open")
    open_mock.return_value.__enter__.return_value = file_mock
    mtime_mock = mocker.patch("os.utime")

    pacman_database.download(url, path)
    request_mock.assert_called_once_with("GET", url, stream=True)
    open_mock.assert_called_once_with("wb")
    file_mock.write.assert_called_once_with("chunk".encode("utf8"))
    mtime_mock.assert_called_once_with(path, (1707438355.0, 1707438355.0))


def test_download_no_header(pacman_database: PacmanDatabase, mocker: MockerFixture) -> None:
    """
    must raise exception in case if no last modified head found
    """
    response_obj = MagicMock()
    response_obj.headers = {}
    mocker.patch("ahriman.core.alpm.pacman_database.PacmanDatabase.make_request", return_value=response_obj)

    with pytest.raises(PacmanError):
        pacman_database.download("url", Path("local"))


def test_is_outdated(pacman_database: PacmanDatabase, mocker: MockerFixture) -> None:
    """
    must correctly check if file is outdated
    """
    response_obj = MagicMock()
    response_obj.headers = {pacman_database.LAST_MODIFIED_HEADER: "Fri, 09 Feb 2024 00:25:55 GMT"}
    stat_mock = MagicMock()
    stat_mock.st_mtime = 1707438354

    path = Path("local")
    url = "url"

    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("ahriman.core.alpm.pacman_database.PacmanDatabase.make_request", return_value=response_obj)
    mocker.patch("pathlib.Path.stat", return_value=stat_mock)

    assert pacman_database.is_outdated(url, path)

    stat_mock.st_mtime += 1
    assert not pacman_database.is_outdated(url, path)

    stat_mock.st_mtime += 1
    assert not pacman_database.is_outdated(url, path)


def test_is_outdated_not_a_file(pacman_database: PacmanDatabase, mocker: MockerFixture) -> None:
    """
    must mark as outdated if no file was found
    """
    mocker.patch("pathlib.Path.is_file", return_value=False)
    assert pacman_database.is_outdated("url", Path("local"))


def test_is_outdated_no_header(pacman_database: PacmanDatabase, mocker: MockerFixture) -> None:
    """
    must raise exception in case if no last modified head found during timestamp check
    """
    response_obj = MagicMock()
    response_obj.headers = {}
    mocker.patch("ahriman.core.alpm.pacman_database.PacmanDatabase.make_request", return_value=response_obj)
    mocker.patch("pathlib.Path.is_file", return_value=True)

    with pytest.raises(PacmanError):
        pacman_database.is_outdated("url", Path("local"))


def test_sync(pacman_database: PacmanDatabase, mocker: MockerFixture) -> None:
    """
    must sync database
    """
    sync_db_mock = mocker.patch("ahriman.core.alpm.pacman_database.PacmanDatabase.sync_packages")
    sync_files_mock = mocker.patch("ahriman.core.alpm.pacman_database.PacmanDatabase.sync_files")

    pacman_database.sync(force=True)
    pacman_database.sync(force=False)
    sync_db_mock.assert_has_calls([MockCall(force=True), MockCall(force=False)])
    sync_files_mock.assert_not_called()


def test_sync_with_files(pacman_database: PacmanDatabase, mocker: MockerFixture) -> None:
    """
    must sync database and files
    """
    sync_db_mock = mocker.patch("ahriman.core.alpm.pacman_database.PacmanDatabase.sync_packages")
    sync_files_mock = mocker.patch("ahriman.core.alpm.pacman_database.PacmanDatabase.sync_files")
    pacman_database.sync_files_database = True

    pacman_database.sync(force=True)
    pacman_database.sync(force=False)
    sync_db_mock.assert_has_calls([MockCall(force=True), MockCall(force=False)])
    sync_files_mock.assert_has_calls([MockCall(force=True), MockCall(force=False)])


def test_sync_exception(pacman_database: PacmanDatabase, mocker: MockerFixture) -> None:
    """
    must suppress all exceptions on failure
    """
    mocker.patch("ahriman.core.alpm.pacman_database.PacmanDatabase.sync_packages", side_effect=Exception())
    pacman_database.sync(force=True)


def test_sync_files(pacman_database: PacmanDatabase, mocker: MockerFixture) -> None:
    """
    must sync files database
    """
    outdated_mock = mocker.patch("ahriman.core.alpm.pacman_database.PacmanDatabase.is_outdated", return_value=True)
    download_mock = mocker.patch("ahriman.core.alpm.pacman_database.PacmanDatabase.download")

    pacman_database.sync_files(force=False)
    outdated_mock.assert_called_once_with(
        "https://geo.mirror.pkgbuild.com/core/os/x86_64/core.files.tar.gz", pytest.helpers.anyvar(int))
    download_mock.assert_called_once_with(
        "https://geo.mirror.pkgbuild.com/core/os/x86_64/core.files.tar.gz", pytest.helpers.anyvar(int))


def test_sync_files_not_outdated(pacman_database: PacmanDatabase, mocker: MockerFixture) -> None:
    """
    must skip files sync if up-to-date
    """
    mocker.patch("ahriman.core.alpm.pacman_database.PacmanDatabase.is_outdated", return_value=False)
    download_mock = mocker.patch("ahriman.core.alpm.pacman_database.PacmanDatabase.download")

    pacman_database.sync_files(force=False)
    download_mock.assert_not_called()


def test_sync_files_force(pacman_database: PacmanDatabase, mocker: MockerFixture) -> None:
    """
    must sync up-to-date files if force flag is set
    """
    mocker.patch("ahriman.core.alpm.pacman_database.PacmanDatabase.is_outdated", return_value=False)
    download_mock = mocker.patch("ahriman.core.alpm.pacman_database.PacmanDatabase.download")

    pacman_database.sync_files(force=True)
    download_mock.assert_called_once_with(
        "https://geo.mirror.pkgbuild.com/core/os/x86_64/core.files.tar.gz", pytest.helpers.anyvar(int))


def test_sync_files_local(pacman_database: PacmanDatabase, mocker: MockerFixture) -> None:
    """
    must copy local files instead of downloading them
    """
    pacman_database.database.servers = ["file:///var"]
    copy_mock = mocker.patch("ahriman.core.alpm.pacman_database.PacmanDatabase.copy")

    pacman_database.sync_files(force=False)
    copy_mock.assert_called_once_with(Path("/var/core.files.tar.gz"), pytest.helpers.anyvar(int))


def test_sync_files_unknown_source(pacman_database: PacmanDatabase) -> None:
    """
    must raise an exception in case if server scheme is unsupported
    """
    pacman_database.database.servers = ["some random string"]
    with pytest.raises(PacmanError):
        pacman_database.sync_files(force=False)


def test_sync_packages(pacman_database: PacmanDatabase) -> None:
    """
    must sync packages by using pyalpm method
    """
    pacman_database.database = MagicMock()

    pacman_database.sync_packages(force=True)
    pacman_database.sync_packages(force=False)
    pacman_database.database.update.assert_has_calls([MockCall(True), MockCall(False)])
