import pytest

from ahriman.core.alpm.aur import AUR


@pytest.fixture
def aur() -> AUR:
    """
    aur helper fixture
    :return: aur helper instance
    """
    return AUR()
