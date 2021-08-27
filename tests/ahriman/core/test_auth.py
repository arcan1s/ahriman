from ahriman.core.auth import Auth
from ahriman.core.configuration import Configuration
from ahriman.models.user import User
from ahriman.models.user_access import UserAccess


def test_get_users(auth: Auth, configuration: Configuration) -> None:
    """
    must return valid user list
    """
    user_write = User("user_write", "pwd_write", UserAccess.Write)
    write_section = Configuration.section_name("auth", user_write.access.value)
    configuration.add_section(write_section)
    configuration.set(write_section, user_write.username, user_write.password)
    user_read = User("user_read", "pwd_read", UserAccess.Read)
    read_section = Configuration.section_name("auth", user_read.access.value)
    configuration.add_section(read_section)
    configuration.set(read_section, user_read.username, user_read.password)

    users = auth.get_users(configuration)
    expected = {user_write.username: user_write, user_read.username: user_read}
    assert users == expected


def test_check_credentials(auth: Auth, user: User) -> None:
    """
    must return true for valid credentials
    """
    current_password = user.password
    user.password = user.generate_password(user.password, auth.salt)
    auth.users[user.username] = user
    assert auth.check_credentials(user.username, current_password)
    assert not auth.check_credentials(user.username, user.password)  # here password is hashed so it is invalid


def test_check_credentials_empty(auth: Auth) -> None:
    """
    must reject on empty credentials
    """
    assert not auth.check_credentials(None, "")
    assert not auth.check_credentials("", None)
    assert not auth.check_credentials(None, None)


def test_check_credentials_unknown(auth: Auth, user: User) -> None:
    """
    must reject on unknown user
    """
    assert not auth.check_credentials(user.username, user.password)


def test_is_safe_request(auth: Auth) -> None:
    """
    must validate safe request
    """
    # login and logout are always safe
    assert auth.is_safe_request("/login")
    assert auth.is_safe_request("/logout")

    auth.allowed_paths.add("/safe")
    auth.allowed_paths_groups.add("/unsafe/safe")

    assert auth.is_safe_request("/safe")
    assert not auth.is_safe_request("/unsafe")
    assert auth.is_safe_request("/unsafe/safe")
    assert auth.is_safe_request("/unsafe/safe/suffix")


def test_is_safe_request_empty(auth: Auth) -> None:
    """
    must not allow requests without path
    """
    assert not auth.is_safe_request(None)
    assert not auth.is_safe_request("")


def test_verify_access(auth: Auth, user: User) -> None:
    """
    must verify user access
    """
    auth.users[user.username] = user
    assert auth.verify_access(user.username, user.access)
    assert not auth.verify_access(user.username, UserAccess.Write)
