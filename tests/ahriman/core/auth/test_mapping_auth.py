import pytest

from ahriman.core.auth.mapping_auth import MappingAuth
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import DuplicateUser
from ahriman.models.user import User
from ahriman.models.user_access import UserAccess


def test_get_users(mapping_auth: MappingAuth, configuration: Configuration) -> None:
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

    users = mapping_auth.get_users(configuration)
    expected = {user_write.username: user_write, user_read.username: user_read}
    assert users == expected


def test_get_users_normalized(mapping_auth: MappingAuth, configuration: Configuration) -> None:
    """
    must return user list with normalized usernames in keys
    """
    user = User("UsEr", "pwd_read", UserAccess.Read)
    read_section = Configuration.section_name("auth", user.access.value)
    configuration.set_option(read_section, user.username, user.password)

    users = mapping_auth.get_users(configuration)
    expected = user.username.lower()
    assert expected in users
    assert users[expected].username == expected


def test_get_users_duplicate(mapping_auth: MappingAuth, configuration: Configuration, user: User) -> None:
    """
    must raise exception on duplicate username
    """
    write_section = Configuration.section_name("auth", UserAccess.Write.value)
    configuration.set_option(write_section, user.username, user.password)
    read_section = Configuration.section_name("auth", UserAccess.Read.value)
    configuration.set_option(read_section, user.username, user.password)

    with pytest.raises(DuplicateUser):
        mapping_auth.get_users(configuration)


def test_check_credentials(mapping_auth: MappingAuth, user: User) -> None:
    """
    must return true for valid credentials
    """
    current_password = user.password
    user.password = user.hash_password(mapping_auth.salt)
    mapping_auth._users[user.username] = user
    assert mapping_auth.check_credentials(user.username, current_password)
    assert not mapping_auth.check_credentials(user.username, user.password)  # here password is hashed so it is invalid


def test_check_credentials_empty(mapping_auth: MappingAuth) -> None:
    """
    must reject on empty credentials
    """
    assert not mapping_auth.check_credentials(None, "")
    assert not mapping_auth.check_credentials("", None)
    assert not mapping_auth.check_credentials(None, None)


def test_check_credentials_unknown(mapping_auth: MappingAuth, user: User) -> None:
    """
    must reject on unknown user
    """
    assert not mapping_auth.check_credentials(user.username, user.password)


def test_get_user(mapping_auth: MappingAuth, user: User) -> None:
    """
    must return user from storage by username
    """
    mapping_auth._users[user.username] = user
    assert mapping_auth.get_user(user.username) == user


def test_get_user_normalized(mapping_auth: MappingAuth, user: User) -> None:
    """
    must return user from storage by username case-insensitive
    """
    mapping_auth._users[user.username] = user
    assert mapping_auth.get_user(user.username.upper()) == user


def test_get_user_unknown(mapping_auth: MappingAuth, user: User) -> None:
    """
    must return None in case if no user found
    """
    assert mapping_auth.get_user(user.username) is None


def test_known_username(mapping_auth: MappingAuth, user: User) -> None:
    """
    must allow only known users
    """
    mapping_auth._users[user.username] = user
    assert mapping_auth.known_username(user.username)
    assert not mapping_auth.known_username(user.password)


def test_verify_access(mapping_auth: MappingAuth, user: User) -> None:
    """
    must verify user access
    """
    mapping_auth._users[user.username] = user
    assert mapping_auth.verify_access(user.username, user.access, None)
    assert not mapping_auth.verify_access(user.username, UserAccess.Write, None)
