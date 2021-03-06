import pytest
import shutil

from pathlib import Path
from pytest_mock import MockerFixture
from unittest import mock

from ahriman.core.repository.cleaner import Cleaner


def _mock_clear(mocker: MockerFixture) -> None:
    mocker.patch("pathlib.Path.iterdir", return_value=[Path("a"), Path("b"), Path("c")])
    mocker.patch("shutil.rmtree")


def _mock_clear_check() -> None:
    shutil.rmtree.assert_has_calls([
        mock.call(Path("a")),
        mock.call(Path("b")),
        mock.call(Path("c"))
    ])


def test_packages_built(cleaner: Cleaner) -> None:
    """
    must raise NotImplemented for missing method
    """
    with pytest.raises(NotImplementedError):
        cleaner.packages_built()


def test_clear_build(cleaner: Cleaner, mocker: MockerFixture) -> None:
    """
    must remove directories with sources
    """
    _mock_clear(mocker)
    cleaner.clear_build()
    _mock_clear_check()


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


def test_clear_manual(cleaner: Cleaner, mocker: MockerFixture) -> None:
    """
    must clear directory with manual packages
    """
    _mock_clear(mocker)
    cleaner.clear_manual()
    _mock_clear_check()


def test_clear_packages(cleaner: Cleaner, mocker: MockerFixture) -> None:
    """
    must delete built packages
    """
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.packages_built",
                 return_value=[Path("a"), Path("b"), Path("c")])
    mocker.patch("pathlib.Path.unlink")

    cleaner.clear_packages()
    Path.unlink.assert_has_calls([mock.call(), mock.call(), mock.call()])
