import pytest

from ahriman.core.auth import Auth
from ahriman.core.configuration import Configuration


@pytest.fixture
def auth(configuration: Configuration) -> Auth:
    """
    auth provider fixture

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        Auth: auth service instance
    """
    return Auth(configuration)
