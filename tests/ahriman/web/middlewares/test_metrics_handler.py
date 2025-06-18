import importlib
import pytest
import sys

from aiohttp.web import HTTPNotFound
from pytest_mock import MockerFixture
from unittest.mock import AsyncMock

import ahriman.web.middlewares.metrics_handler as metrics_handler


async def test_metrics(mocker: MockerFixture) -> None:
    """
    must return metrics methods if library is available
    """
    metrics_mock = AsyncMock()
    mocker.patch.object(metrics_handler, "aiohttp_openmetrics", metrics_mock)

    await metrics_handler.metrics(42)
    metrics_mock.metrics.assert_called_once_with(42)


async def test_metrics_dummy(mocker: MockerFixture) -> None:
    """
    must raise HTTPNotFound if no module found
    """
    mocker.patch.object(metrics_handler, "aiohttp_openmetrics", None)
    with pytest.raises(HTTPNotFound):
        await metrics_handler.metrics(None)


async def test_metrics_handler() -> None:
    """
    must return metrics handler if library is available
    """
    assert metrics_handler.metrics_handler() == metrics_handler.aiohttp_openmetrics.metrics_middleware


async def test_metrics_handler_dummy(mocker: MockerFixture) -> None:
    """
    must return dummy handler if no module found
    """
    mocker.patch.object(metrics_handler, "aiohttp_openmetrics", None)
    handler = metrics_handler.metrics_handler()

    async def handle(result: int) -> int:
        return result

    assert await handler(42, handle) == 42


def test_import_openmetrics_missing(mocker: MockerFixture) -> None:
    """
    must correctly process missing module
    """
    mocker.patch.dict(sys.modules, {"aiohttp_openmetrics": None})
    importlib.reload(metrics_handler)

    assert metrics_handler.aiohttp_openmetrics is None
