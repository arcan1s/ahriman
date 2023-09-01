import pytest

from pathlib import Path
from pyalpm import error as PyalpmError
from pytest_mock import MockerFixture
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.configuration import Configuration
from ahriman.models.pacman_synchronization import PacmanSynchronization
from ahriman.models.repository_paths import RepositoryPaths


def test_init_with_local_cache(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must sync repositories at the start if set
    """
    mocker.patch("ahriman.core.alpm.pacman.Pacman.database_copy")
    sync_mock = mocker.patch("ahriman.core.alpm.pacman.Pacman.database_sync")
    configuration.set_option("alpm", "use_ahriman_cache", "yes")
    _, repository_id = configuration.check_loaded()

    # pyalpm.Handle is trying to reach the directory we've asked, thus we need to patch it a bit
    with TemporaryDirectory(ignore_cleanup_errors=True) as pacman_root:
        mocker.patch.object(RepositoryPaths, "pacman", Path(pacman_root))
        # during the creation pyalpm.Handle will create also version file which we would like to remove later
        pacman = Pacman(repository_id, configuration, refresh_database=PacmanSynchronization.Enabled)
        assert pacman.handle
        sync_mock.assert_called_once_with(pytest.helpers.anyvar(int), force=False)


def test_init_with_local_cache_forced(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must sync repositories at the start if set with force flag
    """
    mocker.patch("ahriman.core.alpm.pacman.Pacman.database_copy")
    sync_mock = mocker.patch("ahriman.core.alpm.pacman.Pacman.database_sync")
    configuration.set_option("alpm", "use_ahriman_cache", "yes")
    _, repository_id = configuration.check_loaded()

    # pyalpm.Handle is trying to reach the directory we've asked, thus we need to patch it a bit
    with TemporaryDirectory(ignore_cleanup_errors=True) as pacman_root:
        mocker.patch.object(RepositoryPaths, "pacman", Path(pacman_root))
        # during the creation pyalpm.Handle will create also version file which we would like to remove later
        pacman = Pacman(repository_id, configuration, refresh_database=PacmanSynchronization.Force)
        assert pacman.handle
        sync_mock.assert_called_once_with(pytest.helpers.anyvar(int), force=True)


def test_database_copy(pacman: Pacman, repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must copy database from root
    """
    database = next(db for db in pacman.handle.get_syncdbs() if db.name == "core")
    path = Path("randomname")
    dst_path = Path("/var/lib/pacman/sync/core.db")
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    # root database exists, local database does not
    mocker.patch("pathlib.Path.is_file", autospec=True, side_effect=lambda p: p.is_relative_to(path))
    mkdir_mock = mocker.patch("pathlib.Path.mkdir")
    copy_mock = mocker.patch("shutil.copy")
    chown_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.chown")

    pacman.database_copy(pacman.handle, database, path, repository_paths, use_ahriman_cache=True)
    mkdir_mock.assert_called_once_with(mode=0o755, exist_ok=True)
    copy_mock.assert_called_once_with(path / "sync" / "core.db", dst_path)
    chown_mock.assert_called_once_with(dst_path)


def test_database_copy_skip(pacman: Pacman, repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must do not copy database from root if local cache is disabled
    """
    database = next(db for db in pacman.handle.get_syncdbs() if db.name == "core")
    path = Path("randomname")
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    # root database exists, local database does not
    mocker.patch("pathlib.Path.is_file", autospec=True, side_effect=lambda p: p.is_relative_to(path))
    copy_mock = mocker.patch("shutil.copy")

    pacman.database_copy(pacman.handle, database, path, repository_paths, use_ahriman_cache=False)
    copy_mock.assert_not_called()


def test_database_copy_no_directory(pacman: Pacman, repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must do not copy database if local cache already exists
    """
    database = next(db for db in pacman.handle.get_syncdbs() if db.name == "core")
    path = Path("randomname")
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    # root database exists, local database does not
    mocker.patch("pathlib.Path.is_file", autospec=True, side_effect=lambda p: p.is_relative_to(path))
    copy_mock = mocker.patch("shutil.copy")

    pacman.database_copy(pacman.handle, database, path, repository_paths, use_ahriman_cache=True)
    copy_mock.assert_not_called()


def test_database_copy_no_root_file(pacman: Pacman, repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must do not copy database if no repository file exists in filesystem
    """
    database = next(db for db in pacman.handle.get_syncdbs() if db.name == "core")
    path = Path("randomname")
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    # root database does not exist, local database does not either
    mocker.patch("pathlib.Path.is_file", return_value=False)
    copy_mock = mocker.patch("shutil.copy")

    pacman.database_copy(pacman.handle, database, path, repository_paths, use_ahriman_cache=True)
    copy_mock.assert_not_called()


def test_database_copy_database_exist(pacman: Pacman, repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must do not copy database if local cache already exists
    """
    database = next(db for db in pacman.handle.get_syncdbs() if db.name == "core")
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    # root database exists, local database does either
    mocker.patch("pathlib.Path.is_file", return_value=True)
    copy_mock = mocker.patch("shutil.copy")

    pacman.database_copy(pacman.handle, database, Path("root"), repository_paths, use_ahriman_cache=True)
    copy_mock.assert_not_called()


def test_database_init(pacman: Pacman, configuration: Configuration) -> None:
    """
    must init database with settings
    """
    mirror = configuration.get("alpm", "mirror")
    database = pacman.database_init(pacman.handle, "testing", mirror, "x86_64")
    assert database.servers == ["https://geo.mirror.pkgbuild.com/testing/os/x86_64"]


def test_database_sync(pacman: Pacman) -> None:
    """
    must sync databases
    """
    handle_mock = MagicMock()
    core_mock = MagicMock()
    extra_mock = MagicMock()
    transaction_mock = MagicMock()
    handle_mock.get_syncdbs.return_value = [core_mock, extra_mock]
    handle_mock.init_transaction.return_value = transaction_mock
    pacman.handle = handle_mock

    pacman.database_sync(pacman.handle, force=False)
    handle_mock.init_transaction.assert_called_once_with()
    core_mock.update.assert_called_once_with(False)
    extra_mock.update.assert_called_once_with(False)
    transaction_mock.release.assert_called_once_with()


def test_database_sync_failed(pacman: Pacman) -> None:
    """
    must sync databases even if there was exception
    """
    handle_mock = MagicMock()
    core_mock = MagicMock()
    core_mock.update.side_effect = PyalpmError()
    extra_mock = MagicMock()
    handle_mock.get_syncdbs.return_value = [core_mock, extra_mock]
    pacman.handle = handle_mock

    pacman.database_sync(pacman.handle, force=False)
    extra_mock.update.assert_called_once_with(False)


def test_database_sync_forced(pacman: Pacman) -> None:
    """
    must sync databases with force flag
    """
    handle_mock = MagicMock()
    core_mock = MagicMock()
    handle_mock.get_syncdbs.return_value = [core_mock]
    pacman.handle = handle_mock

    pacman.database_sync(pacman.handle, force=True)
    handle_mock.init_transaction.assert_called_once_with()
    core_mock.update.assert_called_once_with(True)


def test_package_get(pacman: Pacman) -> None:
    """
    must retrieve package
    """
    assert list(pacman.package_get("pacman"))


def test_package_get_empty(pacman: Pacman) -> None:
    """
    must return empty packages list without exception
    """
    assert not list(pacman.package_get("some-random-name"))


def test_packages(pacman: Pacman) -> None:
    """
    package list must not be empty
    """
    packages = pacman.packages()
    assert packages
    assert "pacman" in packages


def test_packages_with_provides(pacman: Pacman) -> None:
    """
    package list must contain provides packages
    """
    assert "sh" in pacman.packages()
    assert "mysql" in pacman.packages()  # mariadb
