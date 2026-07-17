from ahriman.web.schemas import AuthSchema


def test_schema() -> None:
    """
    must return valid schema
    """
    schema = AuthSchema()
    assert not schema.validate({"AHRIMAN": "key"})
