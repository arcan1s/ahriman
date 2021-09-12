import pytest

from ahriman.core.auth.mapping import Mapping
from ahriman.core.auth.oauth import OAuth
from ahriman.core.configuration import Configuration


@pytest.fixture
def mapping(configuration: Configuration) -> Mapping:
    """
    auth provider fixture
    :param configuration: configuration fixture
    :return: auth service instance
    """
    return Mapping(configuration)


@pytest.fixture
def oauth(configuration: Configuration) -> OAuth:
    """
    OAuth provider fixture
    :param configuration: configuration fixture
    :return: OAuth2 service instance
    """
    configuration.set("web", "address", "https://example.com")
    return OAuth(configuration)
