import pytest

from aiohttp.test_utils import TestClient

from ahriman.models.repository_id import RepositoryId
from ahriman.models.user_access import UserAccess
from ahriman.web.views.v1.status.repositories import RepositoriesView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET",):
        request = pytest.helpers.request("", "", method)
        assert await RepositoriesView.get_permission(request) == UserAccess.Read


def test_routes() -> None:
    """
    must return correct routes
    """
    assert RepositoriesView.ROUTES == ["/api/v1/repositories"]


async def test_get(client: TestClient, repository_id: RepositoryId) -> None:
    """
    must return status for specific package
    """
    response_schema = pytest.helpers.schema_response(RepositoriesView.get)

    response = await client.get(f"/api/v1/repositories")
    assert response.ok
    json = await response.json()
    assert not response_schema.validate(json, many=True)

    assert json == [repository_id.view()]
