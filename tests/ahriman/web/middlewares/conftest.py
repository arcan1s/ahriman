import pytest

from collections import namedtuple

from ahriman.core.auth.auth import Auth
from ahriman.core.configuration import Configuration
from ahriman.models.user import User
from ahriman.web.middlewares.auth_handler import AuthorizationPolicy

_request = namedtuple("_request", ["path", "method"])


@pytest.fixture
def aiohttp_request() -> _request:
    """
    fixture for aiohttp like object
    :return: aiohttp like request test instance
    """
    return _request("path", "GET")


@pytest.fixture
def authorization_policy(configuration: Configuration, user: User) -> AuthorizationPolicy:
    """
    fixture for authorization policy
    :return: authorization policy fixture
    """
    configuration.set("web", "auth", "yes")
    validator = Auth.load(configuration)
    policy = AuthorizationPolicy(validator)
    policy.validator.users = {user.username: user}
    return policy
