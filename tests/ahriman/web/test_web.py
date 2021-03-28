import pytest

from aiohttp import web
from pytest_mock import MockerFixture

from ahriman.core.exceptions import InitializeException
from ahriman.core.status.watcher import Watcher
from ahriman.web.web import on_startup, run_server


@pytest.mark.asyncio
async def test_on_startup(application: web.Application, watcher: Watcher, mocker: MockerFixture) -> None:
    """
    must call load method
    """
    mocker.patch("aiohttp.web.Application.__getitem__", return_value=watcher)
    load_mock = mocker.patch("ahriman.core.status.watcher.Watcher.load")

    await on_startup(application)
    load_mock.assert_called_once()


@pytest.mark.asyncio
async def test_on_startup_exception(application: web.Application, watcher: Watcher, mocker: MockerFixture) -> None:
    """
    must throw exception on load error
    """
    mocker.patch("aiohttp.web.Application.__getitem__", return_value=watcher)
    mocker.patch("ahriman.core.status.watcher.Watcher.load", side_effect=Exception())

    with pytest.raises(InitializeException):
        await on_startup(application)


def test_run(application: web.Application, mocker: MockerFixture) -> None:
    """
    must run application
    """
    host = "localhost"
    port = 8080
    application["config"].set("web", "host", host)
    application["config"].set("web", "port", str(port))
    run_app_mock = mocker.patch("aiohttp.web.run_app")

    run_server(application)
    run_app_mock.assert_called_with(application, host=host, port=port,
                                    handle_signals=False, access_log=pytest.helpers.anyvar(int))
