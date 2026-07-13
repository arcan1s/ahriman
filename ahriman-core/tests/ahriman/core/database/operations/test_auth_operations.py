from ahriman.core.database import SQLite
from ahriman.models.user import User
from ahriman.models.user_access import UserAccess


def test_user_get_update(database: SQLite, user: User) -> None:
    """
    must retrieve user from the database
    """
    database.user_update(user)
    assert database.user_get(user.username) == user


def test_user_list(database: SQLite, user: User) -> None:
    """
    must return all users
    """
    database.user_update(user)
    second = User(username=user.password, password=user.username, access=user.access, packager_id=None, key=None)
    database.user_update(second)

    users = database.user_list(None, None)
    assert len(users) == 2
    assert user in users
    assert second in users


def test_user_list_filter_by_username(database: SQLite) -> None:
    """
    must return users filtered by its id
    """
    first = User(username="1", password="", access=UserAccess.Read, packager_id=None, key=None)
    second = User(username="2", password="", access=UserAccess.Full, packager_id=None, key=None)
    third = User(username="3", password="", access=UserAccess.Read, packager_id=None, key=None)

    database.user_update(first)
    database.user_update(second)
    database.user_update(third)

    assert database.user_list("1", None) == [first]
    assert database.user_list("2", None) == [second]
    assert database.user_list("3", None) == [third]


def test_user_list_filter_by_access(database: SQLite) -> None:
    """
    must return users filtered by its access
    """
    first = User(username="1", password="", access=UserAccess.Read, packager_id=None, key=None)
    second = User(username="2", password="", access=UserAccess.Full, packager_id=None, key=None)
    third = User(username="3", password="", access=UserAccess.Read, packager_id=None, key=None)

    database.user_update(first)
    database.user_update(second)
    database.user_update(third)

    users = database.user_list(None, UserAccess.Read)
    assert len(users) == 2
    assert first in users
    assert third in users


def test_user_list_filter_by_username_access(database: SQLite) -> None:
    """
    must return users filtered by its access and username
    """
    first = User(username="1", password="", access=UserAccess.Read, packager_id=None, key=None)
    second = User(username="2", password="", access=UserAccess.Full, packager_id=None, key=None)
    third = User(username="3", password="", access=UserAccess.Read, packager_id=None, key=None)

    database.user_update(first)
    database.user_update(second)
    database.user_update(third)

    assert database.user_list("1", UserAccess.Read) == [first]
    assert not database.user_list("1", UserAccess.Full)


def test_user_remove_update(database: SQLite, user: User) -> None:
    """
    must remove user from the database
    """
    database.user_update(user)
    database.user_remove(user.username)
    assert database.user_get(user.username) is None


def test_user_update(database: SQLite, user: User) -> None:
    """
    must update user in the database
    """
    database.user_update(user)
    assert database.user_get(user.username) == user

    new_user = User(username=user.username, password=user.hash_password("salt").password, access=UserAccess.Full,
                    packager_id=None, key="new key")
    database.user_update(new_user)
    assert database.user_get(new_user.username) == new_user
