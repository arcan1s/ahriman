from ahriman.models.user_identity import UserIdentity


def test_from_identity(user_identity: UserIdentity) -> None:
    """
    must construct identity object from string
    """
    identity = UserIdentity.from_identity(f"{user_identity.username} {user_identity.expire_at}")
    assert identity == user_identity


def test_from_identity_expired(user_identity: UserIdentity) -> None:
    """
    must construct None from expired identity
    """
    user_identity.expire_at -= 60
    assert UserIdentity.from_identity(f"{user_identity.username} {user_identity.expire_at}") is None


def test_from_identity_no_split() -> None:
    """
    must construct None from invalid string
    """
    assert UserIdentity.from_identity("username") is None


def test_from_identity_not_int() -> None:
    """
    must construct None from invalid timestamp
    """
    assert UserIdentity.from_identity("username timestamp") is None


def test_from_username() -> None:
    """
    must construct identity from username
    """
    identity = UserIdentity.from_username("username", 0)
    assert identity.username == "username"
    # we want to check timestamp too, but later


def test_expire_when() -> None:
    """
    must return correct expiration time
    """
    assert UserIdentity.expire_when(-1) < UserIdentity.expire_when(0) < UserIdentity.expire_when(1)


def test_is_expired(user_identity: UserIdentity) -> None:
    """
    must return expired flag for expired identities
    """
    assert not user_identity.is_expired()

    user_identity.expire_at -= 60
    assert user_identity.is_expired()


def test_to_identity(user_identity: UserIdentity) -> None:
    """
    must return correct identity string
    """
    assert user_identity == UserIdentity.from_identity(user_identity.to_identity())
