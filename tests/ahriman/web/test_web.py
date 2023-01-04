import pytest
import socket

from aiohttp import web
from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.core.exceptions import InitializeError
from ahriman.core.log.filtered_access_logger import FilteredAccessLogger
from ahriman.core.status.watcher import Watcher
from ahriman.web.web import create_socket, on_shutdown, on_startup, run_server


async def test_create_socket(application: web.Application, mocker: MockerFixture) -> None:
    """
    must create socket
    """
    path = "/run/ahriman.sock"
    application["configuration"].set_option("web", "unix_socket", str(path))
    current_on_shutdown = len(application.on_shutdown)

    bind_mock = mocker.patch("socket.socket.bind")
    chmod_mock = mocker.patch("pathlib.Path.chmod")
    unlink_mock = mocker.patch("pathlib.Path.unlink")

    sock = create_socket(application["configuration"], application)
    assert sock.family == socket.AF_UNIX
    assert sock.type == socket.SOCK_STREAM
    bind_mock.assert_called_once_with(str(path))
    chmod_mock.assert_called_once_with(0o666)
    assert len(application.on_shutdown) == current_on_shutdown + 1

    # provoke socket removal
    await application.on_shutdown[-1](application)
    unlink_mock.assert_has_calls([MockCall(missing_ok=True), MockCall(missing_ok=True)])


def test_create_socket_empty(application: web.Application) -> None:
    """
    must skip socket creation if not set by configuration
    """
    assert create_socket(application["configuration"], application) is None


def test_create_socket_safe(application: web.Application, mocker: MockerFixture) -> None:
    """
    must create socket with default permission set
    """
    path = "/run/ahriman.sock"
    application["configuration"].set_option("web", "unix_socket", str(path))
    application["configuration"].set_option("web", "unix_socket_unsafe", "no")

    mocker.patch("socket.socket.bind")
    mocker.patch("pathlib.Path.unlink")
    chmod_mock = mocker.patch("pathlib.Path.chmod")

    sock = create_socket(application["configuration"], application)
    assert sock is not None
    chmod_mock.assert_not_called()


async def test_on_shutdown(application: web.Application, mocker: MockerFixture) -> None:
    """
    must write information to log
    """
    logging_mock = mocker.patch("logging.Logger.warning")
    await on_shutdown(application)
    logging_mock.assert_called_once_with(pytest.helpers.anyvar(str, True))


async def test_on_startup(application: web.Application, watcher: Watcher, mocker: MockerFixture) -> None:
    """
    must call load method
    """
    mocker.patch("aiohttp.web.Application.__getitem__", return_value=watcher)
    load_mock = mocker.patch("ahriman.core.status.watcher.Watcher.load")

    await on_startup(application)
    load_mock.assert_called_once_with()


async def test_on_startup_exception(application: web.Application, watcher: Watcher, mocker: MockerFixture) -> None:
    """
    must throw exception on load error
    """
    mocker.patch("aiohttp.web.Application.__getitem__", return_value=watcher)
    mocker.patch("ahriman.core.status.watcher.Watcher.load", side_effect=Exception())

    with pytest.raises(InitializeError):
        await on_startup(application)


def test_run(application: web.Application, mocker: MockerFixture) -> None:
    """
    must run application
    """
    port = 8080
    application["configuration"].set_option("web", "port", str(port))
    run_application_mock = mocker.patch("aiohttp.web.run_app")

    run_server(application)
    run_application_mock.assert_called_once_with(
        application, host="127.0.0.1", port=port, sock=None, handle_signals=False,
        access_log=pytest.helpers.anyvar(int), access_log_class=FilteredAccessLogger
    )


def test_run_with_auth(application_with_auth: web.Application, mocker: MockerFixture) -> None:
    """
    must run application with enabled authorization
    """
    port = 8080
    application_with_auth["configuration"].set_option("web", "port", str(port))
    run_application_mock = mocker.patch("aiohttp.web.run_app")

    run_server(application_with_auth)
    run_application_mock.assert_called_once_with(
        application_with_auth, host="127.0.0.1", port=port, sock=None, handle_signals=False,
        access_log=pytest.helpers.anyvar(int), access_log_class=FilteredAccessLogger
    )


def test_run_with_debug(application_with_debug: web.Application, mocker: MockerFixture) -> None:
    """
    must run application with enabled debug panel
    """
    port = 8080
    application_with_debug["configuration"].set_option("web", "port", str(port))
    run_application_mock = mocker.patch("aiohttp.web.run_app")

    run_server(application_with_debug)
    run_application_mock.assert_called_once_with(
        application_with_debug, host="127.0.0.1", port=port, sock=None, handle_signals=False,
        access_log=pytest.helpers.anyvar(int), access_log_class=FilteredAccessLogger
    )


def test_run_with_socket(application: web.Application, mocker: MockerFixture) -> None:
    """
    must run application
    """
    port = 8080
    application["configuration"].set_option("web", "port", str(port))
    socket_mock = mocker.patch("ahriman.web.web.create_socket", return_value=42)
    run_application_mock = mocker.patch("aiohttp.web.run_app")

    run_server(application)
    socket_mock.assert_called_once_with(application["configuration"], application)
    run_application_mock.assert_called_once_with(
        application, host="127.0.0.1", port=port, sock=42, handle_signals=False,
        access_log=pytest.helpers.anyvar(int), access_log_class=FilteredAccessLogger
    )
