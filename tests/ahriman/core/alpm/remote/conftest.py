import pytest

from ahriman.core.alpm.remote import AUR, Official, OfficialSyncdb, Remote


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
def official_syncdb() -> OfficialSyncdb:
    """
    official repository fixture with database processing

    Returns:
        OfficialSyncdb: official repository with database processing helper instance
    """
    return OfficialSyncdb()


@pytest.fixture
def remote() -> Remote:
    """
    official repository fixture

    Returns:
        Remote: official repository helper instance
    """
    return Remote()
