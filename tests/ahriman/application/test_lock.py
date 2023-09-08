import argparse
import pytest
import tempfile

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman import __version__
from ahriman.application.lock import Lock
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import DuplicateRunError, UnsafeRunError
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.internal_status import InternalStatus


def test_path(args: argparse.Namespace, configuration: Configuration) -> None:
    """
    must create path variable correctly
    """
    _, repository_id = configuration.check_loaded()

    assert Lock(args, repository_id, configuration).path is None

    args.lock = Path("/run/ahriman.lock")
    assert Lock(args, repository_id, configuration).path == Path("/run/ahriman_aur-clone_x86_64.lock")

    with pytest.raises(ValueError):
        args.lock = Path("/")
        Lock(args, repository_id, configuration).path  # special case


def test_check_version(lock: Lock, mocker: MockerFixture) -> None:
    """
    must check version correctly
    """
    mocker.patch("ahriman.core.status.client.Client.status_get",
                 return_value=InternalStatus(status=BuildStatus(), version=__version__))
    logging_mock = mocker.patch("logging.Logger.warning")

    lock.check_version()
    logging_mock.assert_not_called()


def test_check_version_mismatch(lock: Lock, mocker: MockerFixture) -> None:
    """
    must check mismatched version correctly
    """
    mocker.patch("ahriman.core.status.client.Client.status_get",
                 return_value=InternalStatus(status=BuildStatus(), version="version"))
    logging_mock = mocker.patch("logging.Logger.warning")

    lock.check_version()
    logging_mock.assert_called_once()  # we do not check logging arguments


def test_check_user(lock: Lock, mocker: MockerFixture) -> None:
    """
    must check user correctly
    """
    check_user_patch = mocker.patch("ahriman.application.lock.check_user")
    tree_create = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")

    lock.check_user()
    check_user_patch.assert_called_once_with(lock.paths, unsafe=False)
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

    with pytest.raises(DuplicateRunError):
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


def test_watch(lock: Lock, mocker: MockerFixture) -> None:
    """
    must check if lock file exists
    """
    wait_mock = mocker.patch("ahriman.models.waiter.Waiter.wait")
    lock.path = Path(tempfile.mktemp())  # nosec

    lock.watch()
    wait_mock.assert_called_once_with(lock.path.is_file)


def test_watch_skip(lock: Lock, mocker: MockerFixture) -> None:
    """
    must skip watch on empty path
    """
    mocker.patch("pathlib.Path.is_file", return_value=True)
    lock.watch()


def test_enter(lock: Lock, mocker: MockerFixture) -> None:
    """
    must process with context manager
    """
    check_user_mock = mocker.patch("ahriman.application.lock.Lock.check_user")
    check_version_mock = mocker.patch("ahriman.application.lock.Lock.check_version")
    watch_mock = mocker.patch("ahriman.application.lock.Lock.watch")
    clear_mock = mocker.patch("ahriman.application.lock.Lock.clear")
    create_mock = mocker.patch("ahriman.application.lock.Lock.create")
    update_status_mock = mocker.patch("ahriman.core.status.client.Client.status_update")

    with lock:
        pass
    check_user_mock.assert_called_once_with()
    clear_mock.assert_called_once_with()
    create_mock.assert_called_once_with()
    check_version_mock.assert_called_once_with()
    watch_mock.assert_called_once_with()
    update_status_mock.assert_has_calls([MockCall(BuildStatusEnum.Building), MockCall(BuildStatusEnum.Success)])


def test_exit_with_exception(lock: Lock, mocker: MockerFixture) -> None:
    """
    must process with context manager in case if exception raised
    """
    mocker.patch("ahriman.application.lock.Lock.check_user")
    mocker.patch("ahriman.application.lock.Lock.clear")
    mocker.patch("ahriman.application.lock.Lock.create")
    update_status_mock = mocker.patch("ahriman.core.status.client.Client.status_update")

    with pytest.raises(Exception):
        with lock:
            raise Exception()
    update_status_mock.assert_has_calls([MockCall(BuildStatusEnum.Building), MockCall(BuildStatusEnum.Failed)])
