import pytest

from aiohttp import web
from asyncio import BaseEventLoop
from pytest_aiohttp import TestClient
from pytest_mock import MockerFixture
from typing import Any


@pytest.fixture
def client(application: web.Application, loop: BaseEventLoop,
           aiohttp_client: Any, mocker: MockerFixture) -> TestClient:
    mocker.patch("pathlib.Path.iterdir", return_value=[])
    return loop.run_until_complete(aiohttp_client(application))
