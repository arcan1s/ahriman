import pytest

from multidict import MultiDict
from aiohttp.test_utils import TestClient
from aiohttp.web import HTTPBadRequest, HTTPNotFound
from pytest_mock import MockerFixture
from unittest.mock import AsyncMock

from ahriman.core.configuration import Configuration
from ahriman.models.repository_id import RepositoryId
from ahriman.models.user_access import UserAccess
from ahriman.web.views.base import BaseView


def test_routes() -> None:
    """
    must return correct routes
    """
    assert BaseView.ROUTES == []


def test_configuration(base: BaseView) -> None:
    """
    must return configuration
    """
    assert base.configuration


def test_services(base: BaseView) -> None:
    """
    must return services
    """
    assert base.services


def test_sign(base: BaseView) -> None:
    """
    must return GPP wrapper instance
    """
    assert base.sign


def test_spawn(base: BaseView) -> None:
    """
    must return spawn thread
    """
    assert base.spawner


def test_validator(base: BaseView) -> None:
    """
    must return service
    """
    assert base.validator


async def test_get_permission(base: BaseView) -> None:
    """
    must search for permission attribute in class
    """
    for method in ("DELETE", "GET", "POST"):
        setattr(BaseView, f"{method.upper()}_PERMISSION", "permission")

    for method in ("DELETE", "GET", "HEAD", "POST"):
        request = pytest.helpers.request(base.request.app, "", method)
        assert await base.get_permission(request) == "permission"

    for method in ("OPTIONS",):
        request = pytest.helpers.request(base.request.app, "", method)
        assert await base.get_permission(request) == UserAccess.Unauthorized


def test_get_routes(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must return list of available routes
    """
    routes = ["route1", "route2"]
    mocker.patch.object(BaseView, "ROUTES", routes)
    assert BaseView.routes(configuration) == routes


def test_get_non_empty() -> None:
    """
    must correctly extract non-empty values
    """
    assert BaseView.get_non_empty(lambda k: k, "key")

    with pytest.raises(KeyError):
        BaseView.get_non_empty(lambda k: None, "key")

    with pytest.raises(KeyError):
        BaseView.get_non_empty(lambda k: "", "key")

    assert BaseView.get_non_empty(lambda k: [k], "key")

    with pytest.raises(KeyError):
        BaseView.get_non_empty(lambda k: [], "key")


async def test_head(client: TestClient) -> None:
    """
    must implement head as get method
    """
    response = await client.head("/")
    assert response.ok
    assert await response.text() == ""


async def test_head_not_allowed(client: TestClient) -> None:
    """
    must raise MethodNotAllowed in case if no get method was implemented
    """
    response = await client.head("/api/v1/service/add")
    assert response.status == 405


def test_page(base: BaseView) -> None:
    """
    must extract page from query parameters
    """
    base._request = pytest.helpers.request(base.request.app, "", "", params=MultiDict(limit=2, offset=3))
    assert base.page() == (2, 3)

    base._request = pytest.helpers.request(base.request.app, "", "", params=MultiDict(offset=3))
    assert base.page() == (-1, 3)

    base._request = pytest.helpers.request(base.request.app, "", "", params=MultiDict(limit=2))
    assert base.page() == (2, 0)


def test_page_bad_request(base: BaseView) -> None:
    """
    must raise HTTPBadRequest in case if parameters are invalid
    """
    with pytest.raises(HTTPBadRequest):
        base._request = pytest.helpers.request(base.request.app, "", "", params=MultiDict(limit="string"))
        base.page()

    with pytest.raises(HTTPBadRequest):
        base._request = pytest.helpers.request(base.request.app, "", "", params=MultiDict(offset="string"))
        base.page()

    with pytest.raises(HTTPBadRequest):
        base._request = pytest.helpers.request(base.request.app, "", "", params=MultiDict(limit=-2))
        base.page()

    with pytest.raises(HTTPBadRequest):
        base._request = pytest.helpers.request(base.request.app, "", "", params=MultiDict(offset=-1))
        base.page()


def test_repository_id(base: BaseView, repository_id: RepositoryId) -> None:
    """
    must repository identifier from parameters
    """
    base._request = pytest.helpers.request(base.request.app, "", "",
                                           params=MultiDict(architecture="i686", repository="repo"))
    assert base.repository_id() == RepositoryId("i686", "repo")

    base._request = pytest.helpers.request(base.request.app, "", "", params=MultiDict(architecture="i686"))
    assert base.repository_id() == repository_id

    base._request = pytest.helpers.request(base.request.app, "", "", params=MultiDict(repository="repo"))
    assert base.repository_id() == repository_id

    base._request = pytest.helpers.request(base.request.app, "", "", params=MultiDict())
    assert base.repository_id() == repository_id


def test_service(base: BaseView) -> None:
    """
    must return service for repository
    """
    repository_id = RepositoryId("i686", "repo")
    base.request.app["watcher"] = {
        repository_id: watcher
        for watcher in base.request.app["watcher"].values()
    }

    assert base.service(repository_id) == base.services[repository_id]


def test_service_auto(base: BaseView, repository_id: RepositoryId, mocker: MockerFixture) -> None:
    """
    must return service for repository if no parameters set
    """
    mocker.patch("ahriman.web.views.base.BaseView.repository_id", return_value=repository_id)
    assert base.service() == base.services[repository_id]


def test_service_not_found(base: BaseView) -> None:
    """
    must raise HTTPNotFound if no repository found
    """
    with pytest.raises(HTTPNotFound):
        base.service(RepositoryId("", ""))


async def test_username(base: BaseView, mocker: MockerFixture) -> None:
    """
    must return identity of logged-in user
    """
    policy = AsyncMock()
    policy.identify.return_value = "identity"
    mocker.patch("aiohttp.web.Application.get", return_value=policy)
    json = AsyncMock()
    json.return_value = {}
    base._request = pytest.helpers.request(base.request.app, "", "", json=json)

    assert await base.username() == "identity"
    policy.identify.assert_called_once_with(base.request)


async def test_username_no_auth(base: BaseView) -> None:
    """
    must return None in case if auth is disabled
    """
    json = AsyncMock()
    json.return_value = {}
    base._request = pytest.helpers.request(base.request.app, "", "", json=json)

    assert await base.username() is None


async def test_username_request(base: BaseView) -> None:
    """
    must read packager from request
    """
    json = AsyncMock()
    json.return_value = {"packager": "identity"}
    base._request = pytest.helpers.request(base.request.app, "", "", json=json)

    assert await base.username() == "identity"


async def test_username_request_exception(base: BaseView) -> None:
    """
    must not fail in case if cannot read request
    """
    assert await base.username() is None
