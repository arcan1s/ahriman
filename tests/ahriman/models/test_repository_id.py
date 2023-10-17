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


def test_id() -> None:
    """
    must correctly generate id
    """
    assert RepositoryId("", "").id == "-"
    assert RepositoryId("arch", "repo").id == "arch-repo"


def test_query() -> None:
    """
    must generate query request parameters
    """
    assert RepositoryId("x86_64", "a").query() == [("architecture", "x86_64"), ("repository", "a")]
    assert RepositoryId("i686", "a").query() == [("architecture", "i686"), ("repository", "a")]
    assert RepositoryId("x86_64", "b").query() == [("architecture", "x86_64"), ("repository", "b")]


def test_view() -> None:
    """
    must generate json view
    """
    repository_id = RepositoryId("x86_64", "a")
    assert repository_id.view() == {"architecture": repository_id.architecture, "repository": repository_id.name}

    repository_id = RepositoryId("x86_64", "b")
    assert repository_id.view() == {"architecture": repository_id.architecture, "repository": repository_id.name}

    repository_id = RepositoryId("i686", "a")
    assert repository_id.view() == {"architecture": repository_id.architecture, "repository": repository_id.name}


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
