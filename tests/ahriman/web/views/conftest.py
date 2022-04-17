import pytest

from aiohttp import web
from asyncio import BaseEventLoop
from aiohttp.test_utils import TestClient
from pytest_mock import MockerFixture
from typing import Any
from unittest.mock import MagicMock

from ahriman.core.auth.oauth import OAuth
from ahriman.web.views.base import BaseView


@pytest.fixture
def base(application: web.Application) -> BaseView:
    """
    base view fixture

    Args:
        application(web.Application): application fixture

    Returns:
        BaseView: generated base view fixture
    """
    return BaseView(pytest.helpers.request(application, "", ""))


@pytest.fixture
def client(application: web.Application, event_loop: BaseEventLoop,
           aiohttp_client: Any, mocker: MockerFixture) -> TestClient:
    """
    web client fixture

    Args:
        application(web.Application): application fixture
        event_loop(BaseEventLoop): context event loop
        aiohttp_client(Any): aiohttp client fixture
        mocker(MockerFixture): mocker object

    Returns:
        TestClient: web client test instance
    """
    mocker.patch("pathlib.Path.iterdir", return_value=[])
    return event_loop.run_until_complete(aiohttp_client(application))


@pytest.fixture
def client_with_auth(application_with_auth: web.Application, event_loop: BaseEventLoop,
                     aiohttp_client: Any, mocker: MockerFixture) -> TestClient:
    """
    web client fixture with full authorization functions

    Args:
        application_with_auth(web.Application): application fixture
        event_loop(BaseEventLoop): context event loop
        aiohttp_client(Any): aiohttp client fixture
        mocker(MockerFixture): mocker object

    Returns:
        TestClient: web client test instance
    """
    mocker.patch("pathlib.Path.iterdir", return_value=[])
    return event_loop.run_until_complete(aiohttp_client(application_with_auth))


@pytest.fixture
def client_with_oauth_auth(application_with_auth: web.Application, event_loop: BaseEventLoop,
                           aiohttp_client: Any, mocker: MockerFixture) -> TestClient:
    """
    web client fixture with full authorization functions

    Args:
        application_with_auth(web.Application): application fixture
        event_loop(BaseEventLoop): context event loop
        aiohttp_client(Any): aiohttp client fixture
        mocker(MockerFixture): mocker object

    Returns:
        TestClient: web client test instance
    """
    mocker.patch("pathlib.Path.iterdir", return_value=[])
    application_with_auth["validator"] = MagicMock(spec=OAuth)
    return event_loop.run_until_complete(aiohttp_client(application_with_auth))
