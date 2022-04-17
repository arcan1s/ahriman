import pytest

from ahriman.core.alpm.remote.aur import AUR
from ahriman.core.alpm.remote.official import Official
from ahriman.core.alpm.remote.remote import Remote


@pytest.fixture
def aur() -> AUR:
    """
    aur helper fixture

    Returns:
        AUR: aur helper instance
    """
    return AUR()


@pytest.fixture
def official() -> Official:
    """
    official repository fixture

    Returns:
        Official: official repository helper instance
    """
    return Official()


@pytest.fixture
def remote() -> Remote:
    """
    official repository fixture

    Returns:
        Remote: official repository helper instance
    """
    return Remote()
