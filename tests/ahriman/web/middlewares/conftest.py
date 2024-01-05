import pytest

from ahriman.core.auth import Auth
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.web.middlewares.auth_handler import _AuthorizationPolicy


@pytest.fixture
def authorization_policy(configuration: Configuration, database: SQLite) -> _AuthorizationPolicy:
    """
    fixture for authorization policy

    Args:
        configuration(Configuration): configuration fixture
        database(SQLite): database fixture

    Returns:
        AuthorizationPolicy: authorization policy fixture
    """
    configuration.set_option("auth", "target", "configuration")
    validator = Auth.load(configuration, database)
    policy = _AuthorizationPolicy(validator)
    return policy
