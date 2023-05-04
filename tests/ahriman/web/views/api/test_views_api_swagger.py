import pytest

from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture
from typing import Any

from ahriman.models.user_access import UserAccess
from ahriman.web.views.api.swagger import SwaggerView


def _client(client: TestClient, mocker: MockerFixture) -> TestClient:
    """
    generate test client with docs. Thanks to deprecation, we can't change application state since it was run

    Args:
        client(TestClient): test client fixture
        mocker(MockerFixture): mocker object

    Returns:
        TestClient: test client fixture with additional properties
    """
    swagger_dict = {
        "paths": {
            "/api/v1/logout": {
                "get": {
                    "parameters": [
                        {
                            "in": "cookie",
                            "name": "API_SESSION",
                            "schema": {
                                "type": "string",
                            },
                        },
                    ],
                },
                "head": {},
                "post": {
                    "parameters": [
                        {
                            "in": "cookie",
                            "name": "API_SESSION",
                            "schema": {
                                "type": "string",
                            },
                        },
                        {
                            "in": "body",
                            "name": "schema",
                            "schema": {
                                "type": "string",
                            },
                        },
                    ],
                },
            },
        },
        "components": {},
        "security": [
            {
                "token": {
                    "type": "apiKey",
                    "name": "API_SESSION",
                    "in": "cookie",
                },
            },
        ],
    }
    source = client.app.__getitem__

    def getitem(name: str) -> Any:
        if name == "swagger_dict":
            return swagger_dict
        return source(name)

    mocker.patch("aiohttp.web.Application.__getitem__", side_effect=getitem)

    return client


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET",):
        request = pytest.helpers.request("", "", method)
        assert await SwaggerView.get_permission(request) == UserAccess.Unauthorized


async def test_get(client: TestClient, mocker: MockerFixture) -> None:
    """
    must generate api-docs correctly
    """
    client = _client(client, mocker)
    response = await client.get("/api-docs/swagger.json")
    assert response.ok

    json = await response.json()
    assert "securitySchemes" in json["components"]
    assert not any(parameter["in"] == "body" for parameter in json["paths"]["/api/v1/logout"]["post"]["parameters"])
    assert "requestBody" in json["paths"]["/api/v1/logout"]["post"]
    assert "requestBody" not in json["paths"]["/api/v1/logout"]["get"]
    assert "requestBody" not in json["paths"]["/api/v1/logout"]["head"]
