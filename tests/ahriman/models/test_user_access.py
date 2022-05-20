from pytest_mock import MockerFixture

from ahriman.models.user_access import UserAccess


def test_permits_full() -> None:
    """
    full access must allow everything
    """
    assert UserAccess.Full.permits(UserAccess.Full)
    assert UserAccess.Full.permits(UserAccess.Reporter)
    assert UserAccess.Full.permits(UserAccess.Read)
    assert UserAccess.Full.permits(UserAccess.Unauthorized)


def test_permits_reporter() -> None:
    """
    reporter access must allow everything except full
    """
    assert not UserAccess.Reporter.permits(UserAccess.Full)
    assert UserAccess.Reporter.permits(UserAccess.Reporter)
    assert UserAccess.Reporter.permits(UserAccess.Read)
    assert UserAccess.Reporter.permits(UserAccess.Unauthorized)


def test_permits_read() -> None:
    """
    read access must allow read only and unauthorized
    """
    assert not UserAccess.Read.permits(UserAccess.Full)
    assert not UserAccess.Read.permits(UserAccess.Reporter)
    assert UserAccess.Read.permits(UserAccess.Read)
    assert UserAccess.Read.permits(UserAccess.Unauthorized)


def test_permits_unauthorized() -> None:
    """
    unauthorized access must only allow unauthorized
    """
    assert not UserAccess.Unauthorized.permits(UserAccess.Full)
    assert not UserAccess.Unauthorized.permits(UserAccess.Reporter)
    assert not UserAccess.Unauthorized.permits(UserAccess.Read)
    assert UserAccess.Unauthorized.permits(UserAccess.Unauthorized)


def test_permits_unknown(mocker: MockerFixture) -> None:
    """
    must return False in case if input does not match
    """
    mocker.patch.object(UserAccess, "_member_names_", ["Read"])
    assert not UserAccess.Full.permits(UserAccess.Unauthorized)
