import pytest

from ahriman.models.repository_id import RepositoryId


def test_is_empty() -> None:
    """
    must check if repository id is empty or not
    """
    assert RepositoryId("", "").is_empty
    assert RepositoryId("arch", "").is_empty
    assert RepositoryId("", "repo").is_empty
    assert not RepositoryId("arch", "repo").is_empty


def test_lt() -> None:
    """
    must correctly compare instances
    """
    assert RepositoryId("x86_64", "a") < RepositoryId("x86_64", "b")
    assert RepositoryId("x86_64", "b") > RepositoryId("x86_64", "a")

    assert RepositoryId("i686", "a") < RepositoryId("x86_64", "a")
    assert RepositoryId("x86_64", "a") > RepositoryId("i686", "a")


def test_lt_invalid() -> None:
    """
    must raise ValueError if other is not valid repository id
    """
    with pytest.raises(ValueError):
        RepositoryId("x86_64", "a") < 42
