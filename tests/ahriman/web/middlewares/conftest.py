import pytest

from ahriman.core.auth.auth import Auth
from ahriman.core.configuration import Configuration
from ahriman.models.user import User
from ahriman.web.middlewares.auth_handler import AuthorizationPolicy


@pytest.fixture
def authorization_policy(configuration: Configuration, user: User) -> AuthorizationPolicy:
    """
    fixture for authorization policy
    :return: authorization policy fixture
    """
    configuration.set_option("auth", "target", "configuration")
    validator = Auth.load(configuration)
    policy = AuthorizationPolicy(validator)
    policy.validator._users = {user.username: user}
    return policy
