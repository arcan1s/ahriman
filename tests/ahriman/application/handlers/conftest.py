import pytest

from unittest.mock import MagicMock


@pytest.fixture
def passwd() -> MagicMock:
    """
    get passwd structure for the user

    Returns:
        MagicMock: passwd structure test instance
    """
    passwd = MagicMock()
    passwd.pw_dir = "home"
    return passwd
