import pytest

from ahriman.core.auth import Auth
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.models.user import User
from ahriman.web.middlewares.auth_handler import AuthorizationPolicy


@pytest.fixture
def authorization_policy(configuration: Configuration, database: SQLite, user: User) -> AuthorizationPolicy:
    """
    fixture for authorization policy

    Args:
        configuration(Configuration): configuration fixture
        database(SQLite): database fixture
        user(User): user fixture

    Returns:
        AuthorizationPolicy: authorization policy fixture
    """
    configuration.set_option("auth", "target", "configuration")
    validator = Auth.load(configuration, database)
    policy = AuthorizationPolicy(validator)
    return policy
