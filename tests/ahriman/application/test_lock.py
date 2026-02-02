import argparse
import fcntl
import os
import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from tempfile import NamedTemporaryFile
from unittest.mock import MagicMock, call as MockCall

from ahriman import __version__
from ahriman.application.lock import Lock
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import DuplicateRunError, UnsafeRunError
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.internal_status import InternalStatus
from ahriman.models.repository_id import RepositoryId


def test_path(args: argparse.Namespace, configuration: Configuration) -> None:
    """
    must create path variable correctly
    """
    _, repository_id = configuration.check_loaded()

    assert Lock(args, repository_id, configuration).path is None

    args.lock = Path("/run/ahriman.pid")
    assert Lock(args, repository_id, configuration).path == Path("/run/ahriman_x86_64-aur.pid")

    args.lock = Path("ahriman.pid")
    assert Lock(args, repository_id, configuration).path == Path("/run/ahriman/ahriman_x86_64-aur.pid")

    assert Lock(args, RepositoryId("", ""), configuration).path == Path("/run/ahriman/ahriman.pid")

    with pytest.raises(ValueError):
        args.lock = Path("/")
        assert Lock(args, repository_id, configuration).path  # special case


def test_perform_lock(mocker: MockerFixture) -> None:
    """
    must lock file with fcntl
    """
    flock_mock = mocker.patch("fcntl.flock")
    assert Lock.perform_lock(1)
    flock_mock.assert_called_once_with(1, fcntl.LOCK_EX | fcntl.LOCK_NB)


def test_perform_lock_exception(mocker: MockerFixture) -> None:
    """
    must return False on OSError
    """
    mocker.patch("fcntl.flock", side_effect=OSError)
    assert not Lock.perform_lock(1)


def test_open(lock: Lock, mocker: MockerFixture) -> None:
    """
    must open file
    """
    open_mock = mocker.patch("pathlib.Path.open")
    lock.path = Path("ahriman.pid")

    lock._open()
    open_mock.assert_called_once_with("a+", encoding="utf8")


def test_open_skip(lock: Lock, mocker: MockerFixture) -> None:
    """
    must skip file opening if path is not set
    """
    open_mock = mocker.patch("pathlib.Path.open")
    lock._open()
    open_mock.assert_not_called()


def test_watch(lock: Lock, mocker: MockerFixture) -> None:
    """
    must check if lock file exists
    """
    lock._pid_file = MagicMock()
    lock._pid_file.fileno.return_value = 1
    wait_mock = mocker.patch("ahriman.models.waiter.Waiter.wait")

    lock._watch()
    wait_mock.assert_called_once_with(pytest.helpers.anyvar(int), 1)


def test_watch_skip(lock: Lock, mocker: MockerFixture) -> None:
    """
    must skip watch on empty path
    """
    mocker.patch("ahriman.application.lock.Lock.perform_lock", return_value=True)
    lock._watch()


def test_write(lock: Lock) -> None:
    """
    must write PID to lock file
    """
    with NamedTemporaryFile("a+") as pid_file:
        lock._pid_file = pid_file
        lock._write(is_locked=False)

        assert int(lock._pid_file.readline()) == os.getpid()


def test_write_skip(lock: Lock) -> None:
    """
    must skip write to file if no path set
    """
    lock._write(is_locked=False)


def test_write_locked(lock: Lock, mocker: MockerFixture) -> None:
    """
    must raise DuplicateRunError if it cannot lock file
    """
    mocker.patch("ahriman.application.lock.Lock.perform_lock", return_value=False)
    with pytest.raises(DuplicateRunError):
        lock._pid_file = MagicMock()
        lock._write(is_locked=False)


def test_write_locked_before(lock: Lock, mocker: MockerFixture) -> None:
    """
    must skip lock in case if file was locked before
    """
    lock_mock = mocker.patch("ahriman.application.lock.Lock.perform_lock")
    lock._pid_file = MagicMock()

    lock._write(is_locked=True)
    lock_mock.assert_not_called()


def test_check_user(lock: Lock, mocker: MockerFixture) -> None:
    """
    must check user correctly
    """
    check_user_patch = mocker.patch("ahriman.application.lock.check_user")
    tree_create = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")

    lock.check_user()
    check_user_patch.assert_called_once_with(lock.paths.root, unsafe=False)
    tree_create.assert_called_once_with()


def test_check_user_exception(lock: Lock, mocker: MockerFixture) -> None:
    """
    must raise exception if user differs
    """
    mocker.patch("ahriman.application.lock.check_user", side_effect=UnsafeRunError(0, 1))
    with pytest.raises(UnsafeRunError):
        lock.check_user()


def test_check_user_unsafe(lock: Lock, mocker: MockerFixture) -> None:
    """
    must skip user check if unsafe flag set
    """
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    lock.unsafe = True
    lock.check_user()


def test_check_version(lock: Lock, mocker: MockerFixture) -> None:
    """
    must check version correctly
    """
    mocker.patch("ahriman.core.status.Client.status_get",
                 return_value=InternalStatus(status=BuildStatus(), version=__version__))
    logging_mock = mocker.patch("logging.Logger.warning")

    lock.check_version()
    logging_mock.assert_not_called()


def test_check_version_mismatch(lock: Lock, mocker: MockerFixture) -> None:
    """
    must check mismatched version correctly
    """
    mocker.patch("ahriman.core.status.Client.status_get",
                 return_value=InternalStatus(status=BuildStatus(), version="version"))
    logging_mock = mocker.patch("logging.Logger.warning")

    lock.check_version()
    logging_mock.assert_called_once()  # we do not check logging arguments


def test_clear(lock: Lock) -> None:
    """
    must remove lock file
    """
    lock.path = Path("ahriman-test.pid")
    lock.path.touch()

    lock.clear()
    assert not lock.path.is_file()


def test_clear_missing(lock: Lock) -> None:
    """
    must not fail on lock removal if file is missing
    """
    lock.path = Path("ahriman-test.pid")
    lock.clear()


def test_clear_skip(lock: Lock, mocker: MockerFixture) -> None:
    """
    must skip removal if no file set
    """
    unlink_mock = mocker.patch("pathlib.Path.unlink")
    lock.clear()
    unlink_mock.assert_not_called()


def test_clear_close(lock: Lock) -> None:
    """
    must close pid file if opened
    """
    close_mock = lock._pid_file = MagicMock()
    lock.clear()
    close_mock.close.assert_called_once_with()


def test_clear_close_exception(lock: Lock) -> None:
    """
    must suppress IO exception on file closure
    """
    close_mock = lock._pid_file = MagicMock()
    close_mock.close.side_effect = IOError()
    lock.clear()


def test_lock(lock: Lock, mocker: MockerFixture) -> None:
    """
    must perform lock correctly
    """
    clear_mock = mocker.patch("ahriman.application.lock.Lock.clear")
    open_mock = mocker.patch("ahriman.application.lock.Lock._open")
    watch_mock = mocker.patch("ahriman.application.lock.Lock._watch", return_value=True)
    write_mock = mocker.patch("ahriman.application.lock.Lock._write")

    lock.lock()
    clear_mock.assert_not_called()
    open_mock.assert_called_once_with()
    watch_mock.assert_called_once_with()
    write_mock.assert_called_once_with(is_locked=True)


def test_lock_clear(lock: Lock, mocker: MockerFixture) -> None:
    """
    must clear lock file before lock if force flag is set
    """
    mocker.patch("ahriman.application.lock.Lock._open")
    mocker.patch("ahriman.application.lock.Lock._watch")
    mocker.patch("ahriman.application.lock.Lock._write")
    clear_mock = mocker.patch("ahriman.application.lock.Lock.clear")
    lock.force = True

    lock.lock()
    clear_mock.assert_called_once_with()


def test_enter(lock: Lock, mocker: MockerFixture) -> None:
    """
    must process with context manager
    """
    check_user_mock = mocker.patch("ahriman.application.lock.Lock.check_user")
    check_version_mock = mocker.patch("ahriman.application.lock.Lock.check_version")
    lock_mock = mocker.patch("ahriman.application.lock.Lock.lock")
    update_status_mock = mocker.patch("ahriman.core.status.Client.status_update")

    with lock:
        pass
    check_user_mock.assert_called_once_with()
    check_version_mock.assert_called_once_with()
    lock_mock.assert_called_once_with()
    update_status_mock.assert_has_calls([MockCall(BuildStatusEnum.Building), MockCall(BuildStatusEnum.Success)])


def test_exit_with_exception(lock: Lock, mocker: MockerFixture) -> None:
    """
    must process with context manager in case if exception raised
    """
    mocker.patch("ahriman.application.lock.Lock.check_user")
    mocker.patch("ahriman.application.lock.Lock.clear")
    mocker.patch("ahriman.application.lock.Lock.lock")
    update_status_mock = mocker.patch("ahriman.core.status.Client.status_update")

    with pytest.raises(ValueError):
        with lock:
            raise ValueError()
    update_status_mock.assert_has_calls([MockCall(BuildStatusEnum.Building), MockCall(BuildStatusEnum.Failed)])
