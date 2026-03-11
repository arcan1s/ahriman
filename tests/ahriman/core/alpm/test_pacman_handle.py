import pytest

from pathlib import Path
from unittest.mock import MagicMock

from ahriman.core.alpm.pacman_handle import PacmanHandle


def test_package_load() -> None:
    """
    must load package from archive path
    """
    local = Path("local")
    instance = PacmanHandle.ephemeral()
    handle_mock = instance.handle = MagicMock()

    instance.package_load(local)
    handle_mock.load_pkg.assert_called_once_with(str(local))

    PacmanHandle._ephemeral = None


def test_getattr() -> None:
    """
    must proxy attribute access to underlying handle
    """
    instance = PacmanHandle.ephemeral()
    assert instance.dbpath


def test_getattr_not_found() -> None:
    """
    must raise AttributeError for missing handle attributes
    """
    instance = PacmanHandle.ephemeral()
    with pytest.raises(AttributeError):
        assert instance.random_attribute
