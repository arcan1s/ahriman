import pytest

from ahriman.core.auth.mapping import Mapping
from ahriman.core.auth.oauth import OAuth
from ahriman.core.configuration import Configuration
from ahriman.core.database.sqlite import SQLite


@pytest.fixture
def mapping(configuration: Configuration, database: SQLite) -> Mapping:
    """
    auth provider fixture

    Args:
      configuration(Configuration): configuration fixture
      database(SQLite): database fixture

    Returns:
      Mapping: auth service instance

    Raises:

    """
    return Mapping(configuration, database)


@pytest.fixture
def oauth(configuration: Configuration, database: SQLite) -> OAuth:
    """
    OAuth provider fixture

    Args:
      configuration(Configuration): configuration fixture
      database(SQLite): database fixture

    Returns:
      OAuth: OAuth2 service instance

    Raises:

    """
    configuration.set("web", "address", "https://example.com")
    return OAuth(configuration, database)
