import pytest

from aiohttp.web import Application

from ahriman import __version__
from ahriman.models.repository_id import RepositoryId
from ahriman.web.server_info import server_info
from ahriman.web.views.index import IndexView


async def test_server_info(application: Application, repository_id: RepositoryId) -> None:
    """
    must generate server info
    """
    request = pytest.helpers.request(application, "", "GET")
    view = IndexView(request)
    result = await server_info(view)

    assert result["repositories"] == [{"id": repository_id.id, **repository_id.view()}]
    assert not result["auth"]["enabled"]
    assert not result["auth"]["external"]
    assert result["auth"]["username"] is None
    assert result["auth"]["control"]
    assert result["version"] == __version__
    assert result["autorefresh_intervals"] == []
    assert result["docs_enabled"]
    assert result["index_url"] is None
