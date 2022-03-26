from ahriman.models.user import User
from ahriman.models.user_access import UserAccess


def test_from_option(user: User) -> None:
    """
    must generate user from options
    """
    assert User.from_option(user.username, user.password) == user
    # default is read access
    user.access = UserAccess.Write
    assert User.from_option(user.username, user.password) != user
    assert User.from_option(user.username, user.password, user.access) == user


def test_from_option_empty() -> None:
    """
    must return nothing if settings are missed
    """
    assert User.from_option(None, "") is None
    assert User.from_option("", None) is None
    assert User.from_option(None, None) is None


def test_check_credentials_hash_password(user: User) -> None:
    """
    must generate and validate user password
    """
    current_password = user.password
    user = user.hash_password("salt")
    assert user.check_credentials(current_password, "salt")
    assert not user.check_credentials(current_password, "salt1")
    assert not user.check_credentials(user.password, "salt")


def test_check_credentials_empty_hash(user: User) -> None:
    """
    must reject any authorization if the hash is invalid
    """
    current_password = user.password
    assert not user.check_credentials(current_password, "salt")
    user.password = ""
    assert not user.check_credentials(current_password, "salt")


def test_hash_password_empty_hash(user: User) -> None:
    """
    must return empty string after hash in case if password not set
    """
    user.password = ""
    assert user.hash_password("salt") == user
    user.password = None
    assert user.hash_password("salt") == user


def test_generate_password() -> None:
    """
    must generate password with specified length
    """
    password = User.generate_password(16)
    assert password
    assert len(password) == 16

    password = User.generate_password(42)
    assert password
    assert len(password) == 42


def test_verify_access_read(user: User) -> None:
    """
    user with read access must be able to only request read
    """
    user.access = UserAccess.Read
    assert user.verify_access(UserAccess.Read)
    assert not user.verify_access(UserAccess.Write)


def test_verify_access_write(user: User) -> None:
    """
    user with write access must be able to do anything
    """
    user.access = UserAccess.Write
    assert user.verify_access(UserAccess.Read)
    assert user.verify_access(UserAccess.Write)


def test_repr(user: User) -> None:
    """
    must print user without password
    """
    assert "pa55w0rd" not in str(user)
