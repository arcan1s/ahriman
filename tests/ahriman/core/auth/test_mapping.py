from pytest_mock import MockerFixture

from ahriman.core.auth.mapping import Mapping
from ahriman.models.user import User
from ahriman.models.user_access import UserAccess


async def test_check_credentials(mapping: Mapping, user: User, mocker: MockerFixture) -> None:
    """
    must return true for valid credentials
    """
    current_password = user.password
    user = user.hash_password(mapping.salt)
    mocker.patch("ahriman.core.database.SQLite.user_get", return_value=user)
    assert await mapping.check_credentials(user.username, current_password)
    # here password is hashed so it is invalid
    assert not await mapping.check_credentials(user.username, user.password)


async def test_check_credentials_empty(mapping: Mapping) -> None:
    """
    must reject on empty credentials
    """
    assert not await mapping.check_credentials("", None)


async def test_check_credentials_unknown(mapping: Mapping, user: User) -> None:
    """
    must reject on unknown user
    """
    assert not await mapping.check_credentials(user.username, user.password)


async def test_get_user(mapping: Mapping, user: User, mocker: MockerFixture) -> None:
    """
    must return user from storage by username
    """
    mocker.patch("ahriman.core.database.SQLite.user_get", return_value=user)
    assert await mapping.get_user(user.username) == user


async def test_get_user_normalized(mapping: Mapping, user: User, mocker: MockerFixture) -> None:
    """
    must return user from storage by username case-insensitive
    """
    mocker.patch("ahriman.core.database.SQLite.user_get", return_value=user)
    assert await mapping.get_user(user.username.upper()) == user


async def test_get_user_unknown(mapping: Mapping, user: User) -> None:
    """
    must return None in case if no user found
    """
    assert await mapping.get_user(user.username) is None


async def test_known_username(mapping: Mapping, user: User, mocker: MockerFixture) -> None:
    """
    must allow only known users
    """
    mocker.patch("ahriman.core.database.SQLite.user_get", return_value=user)
    assert await mapping.known_username(user.username)


async def test_known_username_unknown(mapping: Mapping, user: User, mocker: MockerFixture) -> None:
    """
    must not allow unknown users
    """
    mocker.patch("ahriman.core.database.SQLite.user_get", return_value=None)
    assert not await mapping.known_username(user.password)


async def test_verify_access(mapping: Mapping, user: User, mocker: MockerFixture) -> None:
    """
    must verify user access
    """
    mocker.patch("ahriman.core.database.SQLite.user_get", return_value=user)
    assert await mapping.verify_access(user.username, user.access, None)
    assert not await mapping.verify_access(user.username, UserAccess.Full, None)
