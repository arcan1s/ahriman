from pytest_mock import MockerFixture

from ahriman.models.user_access import UserAccess


def test_permits_full() -> None:
    """
    full access must allow everything
    """
    assert UserAccess.FULL.permits(UserAccess.FULL)
    assert UserAccess.FULL.permits(UserAccess.REPORTER)
    assert UserAccess.FULL.permits(UserAccess.READ)
    assert UserAccess.FULL.permits(UserAccess.UNAUTHORIZED)


def test_permits_reporter() -> None:
    """
    reporter access must allow everything except full
    """
    assert not UserAccess.REPORTER.permits(UserAccess.FULL)
    assert UserAccess.REPORTER.permits(UserAccess.REPORTER)
    assert UserAccess.REPORTER.permits(UserAccess.READ)
    assert UserAccess.REPORTER.permits(UserAccess.UNAUTHORIZED)


def test_permits_read() -> None:
    """
    read access must allow read only and unauthorized
    """
    assert not UserAccess.READ.permits(UserAccess.FULL)
    assert not UserAccess.READ.permits(UserAccess.REPORTER)
    assert UserAccess.READ.permits(UserAccess.READ)
    assert UserAccess.READ.permits(UserAccess.UNAUTHORIZED)


def test_permits_unauthorized() -> None:
    """
    unauthorized access must only allow unauthorized
    """
    assert not UserAccess.UNAUTHORIZED.permits(UserAccess.FULL)
    assert not UserAccess.UNAUTHORIZED.permits(UserAccess.REPORTER)
    assert not UserAccess.UNAUTHORIZED.permits(UserAccess.READ)
    assert UserAccess.UNAUTHORIZED.permits(UserAccess.UNAUTHORIZED)


def test_permits_unknown(mocker: MockerFixture) -> None:
    """
    must return False in case if input does not match
    """
    mocker.patch.object(UserAccess, "_member_names_", ["READ"])
    assert not UserAccess.FULL.permits(UserAccess.UNAUTHORIZED)
