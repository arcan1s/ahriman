from aiohttp.web import HTTPFound
from pytest_mock import MockerFixture
from unittest.mock import MagicMock

from ahriman.models.user_access import UserAccess
from ahriman.web.apispec import decorators
from ahriman.web.apispec.decorators import _response_schema, apidocs
from ahriman.web.schemas import LoginSchema


def test_response_schema() -> None:
    """
    must generate response schema
    """
    schema = _response_schema(None)
    assert schema.pop(204)
    assert schema.pop(401)
    assert schema.pop(403)
    assert schema.pop(500)


def test_response_schema_no_403() -> None:
    """
    must generate response schema without 403 error
    """
    schema = _response_schema(None, error_403_enabled=False)
    assert 403 not in schema


def test_response_schema_400() -> None:
    """
    must generate response schema with 400 error
    """
    schema = _response_schema(None, error_400_enabled=True)
    assert schema.pop(400)


def test_response_schema_404() -> None:
    """
    must generate response schema with 404 error
    """
    schema = _response_schema(None, error_404_description="description")
    assert schema.pop(404)


def test_response_schema_200() -> None:
    """
    must generate response schema with 200 response
    """
    schema = _response_schema(LoginSchema)
    response = schema.pop(200)
    assert response["schema"] == LoginSchema
    assert 204 not in schema


def test_response_schema_code() -> None:
    """
    must override status code
    """
    schema = _response_schema(None, response_code=HTTPFound)
    assert schema.pop(302)
    assert 204 not in schema


def test_apidocs() -> None:
    """
    must return decorated function
    """
    annotated = apidocs(
        tags=["tags"],
        summary="summary",
        description="description",
        permission=UserAccess.Unauthorized,
    )(MagicMock())
    assert annotated.__apispec__


def test_apidocs_authorization() -> None:
    """
    must return decorated function with authorization details
    """
    annotated = apidocs(
        tags=["tags"],
        summary="summary",
        description="description",
        permission=UserAccess.Full,
    )(MagicMock())
    assert any(schema["put_into"] == "cookies" for schema in annotated.__schemas__)


def test_apidocs_match() -> None:
    """
    must return decorated function with match details
    """
    annotated = apidocs(
        tags=["tags"],
        summary="summary",
        description="description",
        permission=UserAccess.Unauthorized,
        match_schema=LoginSchema,
    )(MagicMock())
    assert any(schema["put_into"] == "match_info" for schema in annotated.__schemas__)


def test_apidocs_querystring() -> None:
    """
    must return decorated function with query string details
    """
    annotated = apidocs(
        tags=["tags"],
        summary="summary",
        description="description",
        permission=UserAccess.Unauthorized,
        query_schema=LoginSchema,
    )(MagicMock())
    assert any(schema["put_into"] == "querystring" for schema in annotated.__schemas__)


def test_apidocs_json() -> None:
    """
    must return decorated function with json details
    """
    annotated = apidocs(
        tags=["tags"],
        summary="summary",
        description="description",
        permission=UserAccess.Unauthorized,
        body_schema=LoginSchema,
    )(MagicMock())
    assert any(schema["put_into"] == "json" for schema in annotated.__schemas__)


def test_apidocs_form() -> None:
    """
    must return decorated function with generic body details
    """
    annotated = apidocs(
        tags=["tags"],
        summary="summary",
        description="description",
        permission=UserAccess.Unauthorized,
        body_schema=LoginSchema,
        body_location="form",
    )(MagicMock())
    assert any(schema["put_into"] == "form" for schema in annotated.__schemas__)


def test_apidocs_import_error(mocker: MockerFixture) -> None:
    """
    must return same function if no apispec module available
    """
    mocker.patch.object(decorators, "aiohttp_apispec", None)
    mock = MagicMock()

    annotated = apidocs(
        tags=["tags"],
        summary="summary",
        description="description",
        permission=UserAccess.Unauthorized,
    )(mock)
    assert annotated == mock
