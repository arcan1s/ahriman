import pytest

from ahriman.core.auth.auth import Auth
from ahriman.core.configuration import Configuration
from ahriman.core.database.sqlite import SQLite
from ahriman.models.user import User
from ahriman.web.middlewares.auth_handler import AuthorizationPolicy


@pytest.fixture
def authorization_policy(configuration: Configuration, database: SQLite, user: User) -> AuthorizationPolicy:
    """
    fixture for authorization policy
    :return: authorization policy fixture
    """
    configuration.set_option("auth", "target", "configuration")
    validator = Auth.load(configuration, database)
    policy = AuthorizationPolicy(validator)
    return policy
