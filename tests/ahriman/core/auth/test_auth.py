import pytest

from ahriman.core.auth.auth import Auth
from ahriman.core.auth.mapping import Mapping
from ahriman.core.auth.oauth import OAuth
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import DuplicateUser
from ahriman.models.user import User
from ahriman.models.user_access import UserAccess


def test_auth_control(auth: Auth) -> None:
    """
    must return a control for authorization
    """
    assert auth.auth_control
    assert "button" in auth.auth_control  # I think it should be button


def test_load_dummy(configuration: Configuration) -> None:
    """
    must load dummy validator if authorization is not enabled
    """
    configuration.set_option("auth", "target", "disabled")
    auth = Auth.load(configuration)
    assert isinstance(auth, Auth)


def test_load_dummy_empty(configuration: Configuration) -> None:
    """
    must load dummy validator if no option set
    """
    auth = Auth.load(configuration)
    assert isinstance(auth, Auth)


def test_load_mapping(configuration: Configuration) -> None:
    """
    must load mapping validator if option set
    """
    configuration.set_option("auth", "target", "configuration")
    auth = Auth.load(configuration)
    assert isinstance(auth, Mapping)


def test_load_oauth(configuration: Configuration) -> None:
    """
    must load OAuth2 validator if option set
    """
    configuration.set_option("auth", "target", "oauth")
    configuration.set_option("web", "address", "https://example.com")
    auth = Auth.load(configuration)
    assert isinstance(auth, OAuth)


def test_get_users(mapping: Auth, configuration: Configuration) -> None:
    """
    must return valid user list
    """
    user_write = User("user_write", "pwd_write", UserAccess.Write)
    write_section = Configuration.section_name("auth", user_write.access.value)
    configuration.set_option(write_section, user_write.username, user_write.password)
    user_read = User("user_read", "pwd_read", UserAccess.Read)
    read_section = Configuration.section_name("auth", user_read.access.value)
    configuration.set_option(read_section, user_read.username, user_read.password)
    user_read = User("user_read", "pwd_read", UserAccess.Read)
    read_section = Configuration.section_name("auth", user_read.access.value)
    configuration.set_option(read_section, user_read.username, user_read.password)

    users = mapping.get_users(configuration)
    expected = {user_write.username: user_write, user_read.username: user_read}
    assert users == expected


def test_get_users_normalized(mapping: Auth, configuration: Configuration) -> None:
    """
    must return user list with normalized usernames in keys
    """
    user = User("UsEr", "pwd_read", UserAccess.Read)
    read_section = Configuration.section_name("auth", user.access.value)
    configuration.set_option(read_section, user.username, user.password)

    users = mapping.get_users(configuration)
    expected = user.username.lower()
    assert expected in users
    assert users[expected].username == expected


def test_get_users_duplicate(mapping: Auth, configuration: Configuration, user: User) -> None:
    """
    must raise exception on duplicate username
    """
    write_section = Configuration.section_name("auth", UserAccess.Write.value)
    configuration.set_option(write_section, user.username, user.password)
    read_section = Configuration.section_name("auth", UserAccess.Read.value)
    configuration.set_option(read_section, user.username, user.password)

    with pytest.raises(DuplicateUser):
        mapping.get_users(configuration)


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
    assert await auth.verify_access(user.username, UserAccess.Write, None)
