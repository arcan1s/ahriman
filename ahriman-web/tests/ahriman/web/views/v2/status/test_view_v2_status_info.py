import pytest

from aiohttp.test_utils import TestClient

from ahriman import __version__
from ahriman.models.repository_id import RepositoryId
from ahriman.models.user_access import UserAccess
from ahriman.web.views.v2.status.info import InfoView


async def test_get_permission() -> None:
    """
    must return correct permission for the request
    """
    for method in ("GET",):
        request = pytest.helpers.request("", "", method)
        assert await InfoView.get_permission(request) == UserAccess.Unauthorized


def test_routes() -> None:
    """
    must return correct routes
    """
    assert InfoView.ROUTES == ["/api/v2/info"]


async def test_get(client: TestClient, repository_id: RepositoryId) -> None:
    """
    must return service information
    """
    response_schema = pytest.helpers.schema_response(InfoView.get)

    response = await client.get("/api/v2/info")
    assert response.ok
    json = await response.json()
    assert not response_schema.validate(json)

    assert json["repositories"] == [{"id": repository_id.id, **repository_id.view()}]
    assert not json["auth"]["enabled"]
    assert json["auth"]["control"]
    assert json["version"] == __version__
    assert json["autorefresh_intervals"] == []
    assert json["docs_enabled"]
