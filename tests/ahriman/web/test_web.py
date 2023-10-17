import pytest
import socket

from aiohttp.web import Application
from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import InitializeError
from ahriman.core.log.filtered_access_logger import FilteredAccessLogger
from ahriman.core.spawn import Spawn
from ahriman.core.status.watcher import Watcher
from ahriman.web.web import _create_socket, _on_shutdown, _on_startup, run_server, setup_server


async def test_create_socket(application: Application, mocker: MockerFixture) -> None:
    """
    must create socket
    """
    path = "/run/ahriman.sock"
    application["configuration"].set_option("web", "unix_socket", str(path))
    current_on_shutdown = len(application.on_shutdown)

    bind_mock = mocker.patch("socket.socket.bind")
    chmod_mock = mocker.patch("pathlib.Path.chmod")
    unlink_mock = mocker.patch("pathlib.Path.unlink")

    sock = _create_socket(application["configuration"], application)
    assert sock.family == socket.AF_UNIX
    assert sock.type == socket.SOCK_STREAM
    bind_mock.assert_called_once_with(str(path))
    chmod_mock.assert_called_once_with(0o666)
    assert len(application.on_shutdown) == current_on_shutdown + 1

    # provoke socket removal
    await application.on_shutdown[-1](application)
    unlink_mock.assert_has_calls([MockCall(missing_ok=True), MockCall(missing_ok=True)])


def test_create_socket_empty(application: Application) -> None:
    """
    must skip socket creation if not set by configuration
    """
    assert _create_socket(application["configuration"], application) is None


def test_create_socket_safe(application: Application, mocker: MockerFixture) -> None:
    """
    must create socket with default permission set
    """
    path = "/run/ahriman.sock"
    application["configuration"].set_option("web", "unix_socket", str(path))
    application["configuration"].set_option("web", "unix_socket_unsafe", "no")

    mocker.patch("socket.socket.bind")
    mocker.patch("pathlib.Path.unlink")
    chmod_mock = mocker.patch("pathlib.Path.chmod")

    sock = _create_socket(application["configuration"], application)
    assert sock is not None
    chmod_mock.assert_not_called()


async def test_on_shutdown(application: Application, mocker: MockerFixture) -> None:
    """
    must write information to log
    """
    logging_mock = mocker.patch("logging.Logger.warning")
    await _on_shutdown(application)
    logging_mock.assert_called_once_with(pytest.helpers.anyvar(str, True))


async def test_on_startup(application: Application, watcher: Watcher, mocker: MockerFixture) -> None:
    """
    must call load method
    """
    mocker.patch("aiohttp.web.Application.__getitem__", return_value={"": watcher})
    load_mock = mocker.patch("ahriman.core.status.watcher.Watcher.load")

    await _on_startup(application)
    load_mock.assert_called_once_with()


async def test_on_startup_exception(application: Application, watcher: Watcher, mocker: MockerFixture) -> None:
    """
    must throw exception on load error
    """
    mocker.patch("aiohttp.web.Application.__getitem__", return_value={"": watcher})
    mocker.patch("ahriman.core.status.watcher.Watcher.load", side_effect=Exception())

    with pytest.raises(InitializeError):
        await _on_startup(application)


def test_run(application: Application, mocker: MockerFixture) -> None:
    """
    must run application
    """
    port = 8080
    application["configuration"].set_option("web", "port", str(port))
    run_application_mock = mocker.patch("ahriman.web.web.run_app")

    run_server(application)
    run_application_mock.assert_called_once_with(
        application, host="127.0.0.1", port=port, sock=None, handle_signals=True,
        access_log=pytest.helpers.anyvar(int), access_log_class=FilteredAccessLogger
    )


def test_run_with_auth(application_with_auth: Application, mocker: MockerFixture) -> None:
    """
    must run application with enabled authorization
    """
    port = 8080
    application_with_auth["configuration"].set_option("web", "port", str(port))
    run_application_mock = mocker.patch("ahriman.web.web.run_app")

    run_server(application_with_auth)
    run_application_mock.assert_called_once_with(
        application_with_auth, host="127.0.0.1", port=port, sock=None, handle_signals=True,
        access_log=pytest.helpers.anyvar(int), access_log_class=FilteredAccessLogger
    )


@pytest.mark.skip(reason="https://github.com/aio-libs/aiohttp-debugtoolbar/issues/477")
def test_run_with_debug(application_with_debug: Application, mocker: MockerFixture) -> None:
    """
    must run application with enabled debug panel
    """
    port = 8080
    application_with_debug["configuration"].set_option("web", "port", str(port))
    run_application_mock = mocker.patch("ahriman.web.web.run_app")

    run_server(application_with_debug)
    run_application_mock.assert_called_once_with(
        application_with_debug, host="127.0.0.1", port=port, sock=None, handle_signals=True,
        access_log=pytest.helpers.anyvar(int), access_log_class=FilteredAccessLogger
    )


def test_run_with_socket(application: Application, mocker: MockerFixture) -> None:
    """
    must run application
    """
    port = 8080
    application["configuration"].set_option("web", "port", str(port))
    socket_mock = mocker.patch("ahriman.web.web._create_socket", return_value=42)
    run_application_mock = mocker.patch("ahriman.web.web.run_app")

    run_server(application)
    socket_mock.assert_called_once_with(application["configuration"], application)
    run_application_mock.assert_called_once_with(
        application, host="127.0.0.1", port=port, sock=42, handle_signals=True,
        access_log=pytest.helpers.anyvar(int), access_log_class=FilteredAccessLogger
    )


def test_setup_no_repositories(configuration: Configuration, spawner: Spawn) -> None:
    """
    must raise InitializeError if no repositories set
    """
    with pytest.raises(InitializeError):
        setup_server(configuration, spawner, [])
