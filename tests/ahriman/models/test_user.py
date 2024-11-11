import pytest

from dataclasses import replace

from ahriman.models.user import User
from ahriman.models.user_access import UserAccess


def test_algo() -> None:
    """
    must correctly define algorithm used
    """
    assert User(username="user", password=None, access=UserAccess.Read).algo is None
    assert User(username="user", password="", access=UserAccess.Read).algo is None
    assert User(
        username="user",
        password="$6$rounds=656000$mWBiecMPrHAL1VgX$oU4Y5HH8HzlvMaxwkNEJjK13ozElyU1wAHBoO/WW5dAaE4YEfnB0X3FxbynKMl4FBdC3Ovap0jINz4LPkNADg0",
        access=UserAccess.Read,
    ).algo == "$6$"
    assert User(
        username="user",
        password="$2b$12$VCWKazvYxH7B0eAalDGAbu/3y1dSWs79sv/2ujjX1TMaFdVUy80hy",
        access=UserAccess.Read,
    ).algo == "$2b$"


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
    user = replace(user, password="")
    assert not user.check_credentials(current_password, "salt")


def test_check_credentials_sha512() -> None:
    """
    must raise DeprecationWarning for sha512 hashed passwords
    """
    user = User(
        username="user",
        password="$6$rounds=656000$mWBiecMPrHAL1VgX$oU4Y5HH8HzlvMaxwkNEJjK13ozElyU1wAHBoO/WW5dAaE4YEfnB0X3FxbynKMl4FBdC3Ovap0jINz4LPkNADg0",
        access=UserAccess.Read,
    )
    with pytest.raises(ValueError):
        assert user.check_credentials("password", "salt")


def test_hash_password_empty_hash(user: User) -> None:
    """
    must return empty string after hash in case if password not set
    """
    user = replace(user, password="")
    assert user.hash_password("salt") == user
    user = replace(user, password=None)
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
    user = replace(user, access=UserAccess.Read)
    assert user.verify_access(UserAccess.Read)
    assert not user.verify_access(UserAccess.Full)


def test_verify_access_write(user: User) -> None:
    """
    user with write access must be able to do anything
    """
    user = replace(user, access=UserAccess.Full)
    assert user.verify_access(UserAccess.Read)
    assert user.verify_access(UserAccess.Full)


def test_repr(user: User) -> None:
    """
    must print user without password
    """
    assert "pa55w0rd" not in str(user)
