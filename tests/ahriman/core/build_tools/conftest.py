import pytest

from ahriman.core.build_tools.sources import Sources


@pytest.fixture
def sources() -> Sources:
    """
    sources fixture

    Returns:
        Sources: sources instance
    """
    return Sources()
