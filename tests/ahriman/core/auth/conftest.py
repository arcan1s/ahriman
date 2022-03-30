import pytest

from ahriman.core.auth.mapping import Mapping
from ahriman.core.auth.oauth import OAuth
from ahriman.core.configuration import Configuration
from ahriman.core.database.sqlite import SQLite


@pytest.fixture
def mapping(configuration: Configuration, database: SQLite) -> Mapping:
    """
    auth provider fixture
    :param configuration: configuration fixture
    :param database: database fixture
    :return: auth service instance
    """
    return Mapping(configuration, database)


@pytest.fixture
def oauth(configuration: Configuration, database: SQLite) -> OAuth:
    """
    OAuth provider fixture
    :param configuration: configuration fixture
    :param database: database fixture
    :return: OAuth2 service instance
    """
    configuration.set("web", "address", "https://example.com")
    return OAuth(configuration, database)
