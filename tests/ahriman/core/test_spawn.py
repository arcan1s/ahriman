from pytest_mock import MockerFixture
from unittest.mock import MagicMock

from ahriman.core.spawn import Spawn


def test_process(spawner: Spawn) -> None:
    """
    must process external process run correctly
    """
    args = MagicMock()
    callback = MagicMock()
    callback.return_value = True

    spawner.process(callback, args, spawner.architecture, "id", spawner.queue)

    callback.assert_called_with(args, spawner.architecture)
    (uuid, status) = spawner.queue.get()
    assert uuid == "id"
    assert status
    assert spawner.queue.empty()


def test_process_error(spawner: Spawn) -> None:
    """
    must process external run with error correctly
    """
    callback = MagicMock()
    callback.return_value = False

    spawner.process(callback, MagicMock(), spawner.architecture, "id", spawner.queue)

    (uuid, status) = spawner.queue.get()
    assert uuid == "id"
    assert not status
    assert spawner.queue.empty()


def test_packages_add(spawner: Spawn, mocker: MockerFixture) -> None:
    """
    must call package addition
    """
    spawn_mock = mocker.patch("ahriman.core.spawn.Spawn.spawn_process")
    spawner.packages_add(["ahriman", "linux"], now=False)
    spawn_mock.assert_called_with("add", "ahriman", "linux", source="aur")


def test_packages_add_with_build(spawner: Spawn, mocker: MockerFixture) -> None:
    """
    must call package addition with update
    """
    spawn_mock = mocker.patch("ahriman.core.spawn.Spawn.spawn_process")
    spawner.packages_add(["ahriman", "linux"], now=True)
    spawn_mock.assert_called_with("add", "ahriman", "linux", source="aur", now="")


def test_packages_remove(spawner: Spawn, mocker: MockerFixture) -> None:
    """
    must call package removal
    """
    spawn_mock = mocker.patch("ahriman.core.spawn.Spawn.spawn_process")
    spawner.packages_remove(["ahriman", "linux"])
    spawn_mock.assert_called_with("remove", "ahriman", "linux")


def test_spawn_process(spawner: Spawn, mocker: MockerFixture) -> None:
    """
    must correctly spawn child process
    """
    start_mock = mocker.patch("multiprocessing.Process.start")

    spawner.spawn_process("add", "ahriman", now="", maybe="?")
    start_mock.assert_called_once()
    spawner.args_parser.parse_args.assert_called_with([
        "--architecture", spawner.architecture, "--configuration", str(spawner.configuration.path),
        "add", "ahriman", "--now", "--maybe", "?"
    ])


def test_run(spawner: Spawn, mocker: MockerFixture) -> None:
    """
    must implement run method
    """
    logging_mock = mocker.patch("logging.Logger.info")

    spawner.queue.put(("1", False))
    spawner.queue.put(("2", True))
    spawner.queue.put(None)  # terminate

    spawner.run()
    logging_mock.assert_called()


def test_run_pop(spawner: Spawn) -> None:
    """
    must pop and terminate child process
    """
    first = spawner.active["1"] = MagicMock()
    second = spawner.active["2"] = MagicMock()

    spawner.queue.put(("1", False))
    spawner.queue.put(("2", True))
    spawner.queue.put(None)  # terminate

    spawner.run()

    first.terminate.assert_called_once()
    first.join.assert_called_once()
    second.terminate.assert_called_once()
    second.join.assert_called_once()
    assert not spawner.active
