from ahriman.core.auth import Auth
from ahriman.core.auth.mapping import Mapping
from ahriman.core.auth.oauth import OAuth
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.models.user import User
from ahriman.models.user_access import UserAccess


def test_auth_control(auth: Auth) -> None:
    """
    must return a control for authorization
    """
    assert auth.auth_control
    assert "button" in auth.auth_control  # I think it should be a button


def test_load_dummy(configuration: Configuration, database: SQLite) -> None:
    """
    must load dummy validator if authorization is not enabled
    """
    configuration.set_option("auth", "target", "disabled")
    auth = Auth.load(configuration, database)
    assert isinstance(auth, Auth)


def test_load_dummy_empty(configuration: Configuration, database: SQLite) -> None:
    """
    must load dummy validator if no option set
    """
    auth = Auth.load(configuration, database)
    assert isinstance(auth, Auth)


def test_load_mapping(configuration: Configuration, database: SQLite) -> None:
    """
    must load mapping validator if option set
    """
    configuration.set_option("auth", "target", "configuration")
    auth = Auth.load(configuration, database)
    assert isinstance(auth, Mapping)


def test_load_oauth(configuration: Configuration, database: SQLite) -> None:
    """
    must load OAuth2 validator if option set
    """
    configuration.set_option("auth", "target", "oauth")
    configuration.set_option("web", "address", "https://example.com")
    auth = Auth.load(configuration, database)
    assert isinstance(auth, OAuth)


async def test_check_credentials(auth: Auth, user: User) -> None:
    """
    must pass any credentials
    """
    assert await auth.check_credentials(user.username, user.password)
    assert await auth.check_credentials(None, "")
    assert await auth.check_credentials("", None)
    assert await auth.check_credentials(None, None)


async def test_known_username(auth: Auth, user: User) -> None:
    """
    must allow any username
    """
    assert await auth.known_username(user.username)


async def test_verify_access(auth: Auth, user: User) -> None:
    """
    must allow any access
    """
    assert await auth.verify_access(user.username, user.access, None)
    assert await auth.verify_access(user.username, UserAccess.Full, None)
