from ahriman.web.schemas.auth_schema import AuthSchema


def test_schema() -> None:
    """
    must return valid schema
    """
    schema = AuthSchema()
    assert not schema.validate({"API_SESSION": "key"})
