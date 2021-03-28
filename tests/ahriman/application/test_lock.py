import pytest
import tempfile

from pathlib import Path
from pytest_mock import MockerFixture
from unittest import mock

from ahriman.application.lock import Lock
from ahriman.core.exceptions import DuplicateRun, UnsafeRun
from ahriman.models.build_status import BuildStatusEnum


def test_enter(lock: Lock, mocker: MockerFixture) -> None:
    """
    must process with context manager
    """
    check_user_mock = mocker.patch("ahriman.application.lock.Lock.check_user")
    remove_mock = mocker.patch("ahriman.application.lock.Lock.remove")
    create_mock = mocker.patch("ahriman.application.lock.Lock.create")
    update_status_mock = mocker.patch("ahriman.core.status.client.Client.update_self")

    with lock:
        pass
    check_user_mock.assert_called_once()
    remove_mock.assert_called_once()
    create_mock.assert_called_once()
    update_status_mock.assert_has_calls([
        mock.call(BuildStatusEnum.Building),
        mock.call(BuildStatusEnum.Success)
    ])


def test_exit_with_exception(lock: Lock, mocker: MockerFixture) -> None:
    """
    must process with context manager in case if exception raised
    """
    mocker.patch("ahriman.application.lock.Lock.check_user")
    mocker.patch("ahriman.application.lock.Lock.remove")
    mocker.patch("ahriman.application.lock.Lock.create")
    update_status_mock = mocker.patch("ahriman.core.status.client.Client.update_self")

    with pytest.raises(Exception):
        with lock:
            raise Exception()
    update_status_mock.assert_has_calls([
        mock.call(BuildStatusEnum.Building),
        mock.call(BuildStatusEnum.Failed)
    ])


def test_check_user(lock: Lock, mocker: MockerFixture) -> None:
    """
    must check user correctly
    """
    stat = Path.cwd().stat()
    mocker.patch("pathlib.Path.stat", return_value=stat)
    mocker.patch("os.getuid", return_value=stat.st_uid)

    lock.check_user()


def test_check_user_exception(lock: Lock, mocker: MockerFixture) -> None:
    """
    must raise exception if user differs
    """
    stat = Path.cwd().stat()
    mocker.patch("pathlib.Path.stat")
    mocker.patch("os.getuid", return_value=stat.st_uid + 1)

    with pytest.raises(UnsafeRun):
        lock.check_user()


def test_check_user_unsafe(lock: Lock) -> None:
    """
    must skip user check if unsafe flag set
    """
    lock.unsafe = True
    lock.check_user()


def test_create(lock: Lock) -> None:
    """
    must create lock
    """
    lock.path = Path(tempfile.mktemp())

    lock.create()
    assert lock.path.is_file()
    lock.path.unlink()


def test_create_exception(lock: Lock) -> None:
    """
    must raise exception if file already exists
    """
    lock.path = Path(tempfile.mktemp())
    lock.path.touch()

    with pytest.raises(DuplicateRun):
        lock.create()
    lock.path.unlink()


def test_create_skip(lock: Lock, mocker: MockerFixture) -> None:
    """
    must skip creating if no file set
    """
    touch_mock = mocker.patch("pathlib.Path.touch")
    lock.create()
    touch_mock.assert_not_called()


def test_create_unsafe(lock: Lock) -> None:
    """
    must not raise exception if force flag set
    """
    lock.force = True
    lock.path = Path(tempfile.mktemp())
    lock.path.touch()

    lock.create()
    lock.path.unlink()


def test_remove(lock: Lock) -> None:
    """
    must remove lock file
    """
    lock.path = Path(tempfile.mktemp())
    lock.path.touch()

    lock.remove()
    assert not lock.path.is_file()


def test_remove_missing(lock: Lock) -> None:
    """
    must not fail on lock removal if file is missing
    """
    lock.path = Path(tempfile.mktemp())
    lock.remove()


def test_remove_skip(lock: Lock, mocker: MockerFixture) -> None:
    """
    must skip removal if no file set
    """
    unlink_mock = mocker.patch("pathlib.Path.unlink")
    lock.remove()
    unlink_mock.assert_not_called()
