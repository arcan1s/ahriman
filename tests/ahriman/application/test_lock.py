import pytest
import tempfile

from pathlib import Path
from pytest_mock import MockerFixture
from unittest import mock

from ahriman import version
from ahriman.application.lock import Lock
from ahriman.core.exceptions import DuplicateRun, UnsafeRun
from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.internal_status import InternalStatus


def test_enter(lock: Lock, mocker: MockerFixture) -> None:
    """
    must process with context manager
    """
    check_user_mock = mocker.patch("ahriman.application.lock.Lock.check_user")
    check_version_mock = mocker.patch("ahriman.application.lock.Lock.check_version")
    clear_mock = mocker.patch("ahriman.application.lock.Lock.clear")
    create_mock = mocker.patch("ahriman.application.lock.Lock.create")
    update_status_mock = mocker.patch("ahriman.core.status.client.Client.update_self")

    with lock:
        pass
    check_user_mock.assert_called_once()
    clear_mock.assert_called_once()
    create_mock.assert_called_once()
    check_version_mock.assert_called_once()
    update_status_mock.assert_has_calls([
        mock.call(BuildStatusEnum.Building),
        mock.call(BuildStatusEnum.Success)
    ])


def test_exit_with_exception(lock: Lock, mocker: MockerFixture) -> None:
    """
    must process with context manager in case if exception raised
    """
    mocker.patch("ahriman.application.lock.Lock.check_user")
    mocker.patch("ahriman.application.lock.Lock.clear")
    mocker.patch("ahriman.application.lock.Lock.create")
    update_status_mock = mocker.patch("ahriman.core.status.client.Client.update_self")

    with pytest.raises(Exception):
        with lock:
            raise Exception()
    update_status_mock.assert_has_calls([
        mock.call(BuildStatusEnum.Building),
        mock.call(BuildStatusEnum.Failed)
    ])


def test_check_version(lock: Lock, mocker: MockerFixture) -> None:
    """
    must check version correctly
    """
    mocker.patch("ahriman.core.status.client.Client.get_internal",
                 return_value=InternalStatus(version=version.__version__))
    logging_mock = mocker.patch("logging.Logger.warning")

    lock.check_version()
    logging_mock.assert_not_called()


def test_check_version_mismatch(lock: Lock, mocker: MockerFixture) -> None:
    """
    must check version correctly
    """
    mocker.patch("ahriman.core.status.client.Client.get_internal",
                 return_value=InternalStatus(version="version"))
    logging_mock = mocker.patch("logging.Logger.warning")

    lock.check_version()
    logging_mock.assert_called_once()


def test_check_user(lock: Lock, mocker: MockerFixture) -> None:
    """
    must check user correctly
    """
    check_user_patch = mocker.patch("ahriman.application.lock.check_user")
    lock.check_user()
    check_user_patch.assert_called_once_with(lock.root)


def test_check_user_exception(lock: Lock, mocker: MockerFixture) -> None:
    """
    must raise exception if user differs
    """
    mocker.patch("ahriman.application.lock.check_user", side_effect=UnsafeRun(0, 1))
    with pytest.raises(UnsafeRun):
        lock.check_user()


def test_check_user_unsafe(lock: Lock) -> None:
    """
    must skip user check if unsafe flag set
    """
    lock.unsafe = True
    lock.check_user()


def test_clear(lock: Lock) -> None:
    """
    must remove lock file
    """
    lock.path = Path(tempfile.mktemp())  # nosec
    lock.path.touch()

    lock.clear()
    assert not lock.path.is_file()


def test_clear_missing(lock: Lock) -> None:
    """
    must not fail on lock removal if file is missing
    """
    lock.path = Path(tempfile.mktemp())  # nosec
    lock.clear()


def test_clear_skip(lock: Lock, mocker: MockerFixture) -> None:
    """
    must skip removal if no file set
    """
    unlink_mock = mocker.patch("pathlib.Path.unlink")
    lock.clear()
    unlink_mock.assert_not_called()


def test_create(lock: Lock) -> None:
    """
    must create lock
    """
    lock.path = Path(tempfile.mktemp())  # nosec

    lock.create()
    assert lock.path.is_file()
    lock.path.unlink()


def test_create_exception(lock: Lock) -> None:
    """
    must raise exception if file already exists
    """
    lock.path = Path(tempfile.mktemp())  # nosec
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
    lock.path = Path(tempfile.mktemp())  # nosec
    lock.path.touch()

    lock.create()
    lock.path.unlink()
