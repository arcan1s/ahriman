from ahriman.models.context_key import ContextKey


def test_from_type() -> None:
    """
    must construct key from type
    """
    assert ContextKey.from_type(int) == ContextKey("int", int)
    assert ContextKey.from_type(ContextKey) == ContextKey("ContextKey", ContextKey)
