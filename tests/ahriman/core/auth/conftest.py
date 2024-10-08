import pytest

from ahriman.core.auth.mapping import Mapping
from ahriman.core.auth.oauth import OAuth
from ahriman.core.auth.pam import PAM
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite


@pytest.fixture
def mapping(configuration: Configuration, database: SQLite) -> Mapping:
    """
    auth provider fixture

    Args:
        configuration(Configuration): configuration fixture
        database(SQLite): database fixture

    Returns:
        Mapping: auth service instance
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
    """
    configuration.set("web", "address", "https://example.com")
    return OAuth(configuration, database)


@pytest.fixture
def pam(configuration: Configuration, database: SQLite) -> PAM:
    """
    PAM provider fixture

    Args:
        configuration(Configuration): configuration fixture
        database(SQLite): database fixture

    Returns:
        PAM: PAM service instance
    """
    configuration.set_option("auth", "full_access_group", "wheel")
    return PAM(configuration, database)
