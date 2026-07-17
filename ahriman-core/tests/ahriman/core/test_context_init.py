import pytest

from ahriman.core import _Context
from ahriman.models.context_key import ContextKey


def test_get_set() -> None:
    """
    must set and get variable
    """
    key, value = ContextKey("key", int), 42
    ctx = _Context()

    ctx.set(key, value)
    assert ctx.get(key) == value


def test_get_set_type() -> None:
    """
    must set and get variable by type
    """
    key, value = int, 42
    ctx = _Context()

    ctx.set(key, value)
    assert ctx.get(key) == value
    assert ctx.get(ContextKey.from_type(int)) == value


def test_get_key_exception() -> None:
    """
    must raise KeyError in case if key was not found
    """
    ctx = _Context()
    with pytest.raises(KeyError):
        ctx.get(ContextKey("key", int))


def test_get_value_exception() -> None:
    """
    must raise ValueError in case if key type differs from existing value
    """
    key, value = ContextKey("key", int), 42
    ctx = _Context()
    ctx.set(key, value)

    with pytest.raises(ValueError):
        ctx.get(ContextKey("key", str))


def test_set_key_exception() -> None:
    """
    must raise KeyError in case if key already exists
    """
    key, value = ContextKey("key", int), 42
    ctx = _Context()
    ctx.set(key, value)

    with pytest.raises(KeyError):
        ctx.set(key, value)


def test_set_value_exception() -> None:
    """
    must raise ValueError in case if key type differs from new value
    """
    ctx = _Context()
    with pytest.raises(ValueError):
        ctx.set(ContextKey("key", str), 42)


def test_contains() -> None:
    """
    must correctly check if element is in list
    """
    key, value = ContextKey("key", int), 42
    ctx = _Context()
    ctx.set(key, value)

    assert key not in ctx
    assert key.key in ctx
    assert "random-key" not in ctx


def test_iter() -> None:
    """
    must return keys iterator
    """
    key, value = ContextKey("key", int), 42
    ctx = _Context()
    ctx.set(key, value)

    assert set(iter(ctx)) == set(iter({key.key: value}))


def test_len() -> None:
    """
    must correctly define collection length
    """
    ctx = _Context()
    ctx.set(ContextKey("str", str), "str")
    ctx.set(ContextKey("int", int), 42)

    assert len(ctx) == 2
