import pyalpm
import pytest
import tarfile

from pathlib import Path
from pytest_mock import MockerFixture
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, call as MockCall

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.configuration import Configuration
from ahriman.models.package import Package
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


def test_database_copy(pacman: Pacman, mocker: MockerFixture) -> None:
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

    pacman.database_copy(pacman.handle, database, path, use_ahriman_cache=True)
    mkdir_mock.assert_called_once_with(mode=0o755, exist_ok=True)
    copy_mock.assert_called_once_with(path / "sync" / "core.db", dst_path)
    chown_mock.assert_called_once_with(dst_path)


def test_database_copy_skip(pacman: Pacman, mocker: MockerFixture) -> None:
    """
    must do not copy database from root if local cache is disabled
    """
    database = next(db for db in pacman.handle.get_syncdbs() if db.name == "core")
    path = Path("randomname")
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    # root database exists, local database does not
    mocker.patch("pathlib.Path.is_file", autospec=True, side_effect=lambda p: p.is_relative_to(path))
    copy_mock = mocker.patch("shutil.copy")

    pacman.database_copy(pacman.handle, database, path, use_ahriman_cache=False)
    copy_mock.assert_not_called()


def test_database_copy_no_directory(pacman: Pacman, mocker: MockerFixture) -> None:
    """
    must do not copy database if directory does not exist
    """
    database = next(db for db in pacman.handle.get_syncdbs() if db.name == "core")
    path = Path("randomname")
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    # root database exists, local database does not
    mocker.patch("pathlib.Path.is_file", autospec=True, side_effect=lambda p: p.is_relative_to(path))
    copy_mock = mocker.patch("shutil.copy")

    pacman.database_copy(pacman.handle, database, path, use_ahriman_cache=True)
    copy_mock.assert_not_called()


def test_database_copy_no_root_file(pacman: Pacman, mocker: MockerFixture) -> None:
    """
    must do not copy database if no repository file exists in filesystem
    """
    database = next(db for db in pacman.handle.get_syncdbs() if db.name == "core")
    path = Path("randomname")
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    # root database does not exist, local database does not either
    mocker.patch("pathlib.Path.is_file", return_value=False)
    copy_mock = mocker.patch("shutil.copy")

    pacman.database_copy(pacman.handle, database, path, use_ahriman_cache=True)
    copy_mock.assert_not_called()


def test_database_copy_database_exist(pacman: Pacman, mocker: MockerFixture) -> None:
    """
    must do not copy database if local cache already exists
    """
    database = next(db for db in pacman.handle.get_syncdbs() if db.name == "core")
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    # root database exists, local database does either
    mocker.patch("pathlib.Path.is_file", return_value=True)
    copy_mock = mocker.patch("shutil.copy")

    pacman.database_copy(pacman.handle, database, Path("root"), use_ahriman_cache=True)
    copy_mock.assert_not_called()


def test_database_init(pacman: Pacman) -> None:
    """
    must init database with settings
    """
    database = pacman.database_init(pacman.handle, "testing", "x86_64")
    assert database.servers == ["https://geo.mirror.pkgbuild.com/testing/os/x86_64"]


def test_database_init_local(pacman: Pacman, configuration: Configuration) -> None:
    """
    must set file protocol for local databases
    """
    _, repository_id = configuration.check_loaded()
    database = pacman.database_init(MagicMock(), repository_id.name, repository_id.architecture)
    assert database.servers == [f"file://{configuration.repository_paths.repository}"]


def test_database_sync(pacman: Pacman, mocker: MockerFixture) -> None:
    """
    must sync databases
    """
    handle_mock = MagicMock()
    transaction_mock = MagicMock()
    handle_mock.get_syncdbs.return_value = [1, 2]
    handle_mock.init_transaction.return_value = transaction_mock

    sync_mock = mocker.patch("ahriman.core.alpm.pacman_database.PacmanDatabase.sync")

    pacman.database_sync(handle_mock, force=False)
    handle_mock.init_transaction.assert_called_once_with()
    sync_mock.assert_has_calls([MockCall(force=False), MockCall(force=False)])
    transaction_mock.release.assert_called_once_with()


def test_database_sync_forced(pacman: Pacman, mocker: MockerFixture) -> None:
    """
    must sync databases with force flag
    """
    handle_mock = MagicMock()
    handle_mock.get_syncdbs.return_value = [1]

    sync_mock = mocker.patch("ahriman.core.alpm.pacman_database.PacmanDatabase.sync")

    pacman.database_sync(handle_mock, force=True)
    sync_mock.assert_called_once_with(force=True)


def test_files_package(pacman: Pacman, package_ahriman: Package, pyalpm_package_ahriman: pyalpm.Package,
                       mocker: MockerFixture, resource_path_root: Path) -> None:
    """
    must load files only for the specified package
    """
    mocker.patch("ahriman.core.alpm.pacman.Pacman.package", return_value=[pyalpm_package_ahriman])
    handle_mock = MagicMock()
    handle_mock.get_syncdbs.return_value = [MagicMock()]
    pacman.handle = handle_mock

    tarball = resource_path_root / "core" / "arcanisrepo.files.tar.gz"

    with tarfile.open(tarball, "r:gz") as fd:
        mocker.patch("pathlib.Path.is_file", return_value=True)
        mocker.patch("ahriman.core.alpm.pacman.tarfile.open", return_value=fd)

        files = pacman.files([package_ahriman.base])
        assert len(files) == 1
        assert package_ahriman.base in files


def test_files_skip(pacman: Pacman, pyalpm_package_ahriman: pyalpm.Package, mocker: MockerFixture) -> None:
    """
    must return empty list if no database found
    """
    mocker.patch("ahriman.core.alpm.pacman.Pacman.package", return_value=[pyalpm_package_ahriman])
    handle_mock = MagicMock()
    handle_mock.get_syncdbs.return_value = [MagicMock()]
    pacman.handle = handle_mock

    mocker.patch("pathlib.Path.is_file", return_value=False)

    assert not pacman.files([pyalpm_package_ahriman.name])


def test_files_no_content(pacman: Pacman, pyalpm_package_ahriman: pyalpm.Package, mocker: MockerFixture) -> None:
    """
    must skip package if no content can be loaded
    """
    mocker.patch("ahriman.core.alpm.pacman.Pacman.package", return_value=[pyalpm_package_ahriman])
    handle_mock = MagicMock()
    handle_mock.get_syncdbs.return_value = [MagicMock()]
    pacman.handle = handle_mock

    tar_mock = MagicMock()
    tar_mock.extractfile.return_value = None

    open_mock = MagicMock()
    open_mock.__enter__.return_value = tar_mock

    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("ahriman.core.alpm.pacman.tarfile.open", return_value=open_mock)

    assert not pacman.files([pyalpm_package_ahriman.name])


def test_files_no_entry(pacman: Pacman, pyalpm_package_ahriman: pyalpm.Package, mocker: MockerFixture) -> None:
    """
    must skip package if it wasn't found in the archive
    """
    mocker.patch("ahriman.core.alpm.pacman.Pacman.package", return_value=[pyalpm_package_ahriman])
    handle_mock = MagicMock()
    handle_mock.get_syncdbs.return_value = [MagicMock()]
    pacman.handle = handle_mock

    tar_mock = MagicMock()
    tar_mock.extractfile.side_effect = KeyError()

    open_mock = MagicMock()
    open_mock.__enter__.return_value = tar_mock

    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("ahriman.core.alpm.pacman.tarfile.open", return_value=open_mock)

    assert not pacman.files([pyalpm_package_ahriman.name])


def test_package(pacman: Pacman) -> None:
    """
    must retrieve package
    """
    assert list(pacman.package("pacman"))


def test_package_empty(pacman: Pacman) -> None:
    """
    must return empty packages list without exception
    """
    assert not list(pacman.package("some-random-name"))


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
