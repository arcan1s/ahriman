import pytest
import shutil

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.core.repository.cleaner import Cleaner


def _mock_clear(mocker: MockerFixture) -> None:
    """
    mocker helper for clear function

    Args:
        mocker(MockerFixture): mocker object
    """
    mocker.patch("pathlib.Path.iterdir", return_value=[Path("a"), Path("b"), Path("c")])
    mocker.patch("shutil.rmtree")


def _mock_clear_check() -> None:
    """
    mocker helper for clear tests
    """
    shutil.rmtree.assert_has_calls([
        MockCall(Path("a")),
        MockCall(Path("b")),
        MockCall(Path("c"))
    ])


def test_clear_cache(cleaner: Cleaner, mocker: MockerFixture) -> None:
    """
    must remove every cached sources
    """
    _mock_clear(mocker)
    cleaner.clear_cache()
    _mock_clear_check()


def test_clear_chroot(cleaner: Cleaner, mocker: MockerFixture) -> None:
    """
    must clear chroot
    """
    _mock_clear(mocker)
    cleaner.clear_chroot()
    _mock_clear_check()


def test_clear_packages(cleaner: Cleaner, mocker: MockerFixture) -> None:
    """
    must delete built packages
    """
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.packages_built",
                 return_value=[Path("a"), Path("b"), Path("c")])
    mocker.patch("pathlib.Path.unlink")

    cleaner.clear_packages()
    Path.unlink.assert_has_calls([MockCall(), MockCall(), MockCall()])


def test_clear_pacman(cleaner: Cleaner, mocker: MockerFixture) -> None:
    """
    must clear pacman root
    """
    _mock_clear(mocker)
    cleaner.clear_pacman()
    _mock_clear_check()


def test_clear_queue(cleaner: Cleaner, mocker: MockerFixture) -> None:
    """
    must clear queued packages from the database
    """
    clear_mock = mocker.patch("ahriman.core.database.SQLite.build_queue_clear")
    cleaner.clear_queue()
    clear_mock.assert_called_once_with(None)


def test_packages_built(cleaner: Cleaner) -> None:
    """
    must raise NotImplemented for missing method
    """
    with pytest.raises(NotImplementedError):
        cleaner.packages_built()
