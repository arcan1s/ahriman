import pytest

from collections import namedtuple


_passwd = namedtuple("passwd", ["pw_dir"])


@pytest.fixture
def passwd() -> _passwd:
    """
    get passwd structure for the user

    Returns:
        _passwd: passwd structure test instance
    """
    return _passwd("home")
