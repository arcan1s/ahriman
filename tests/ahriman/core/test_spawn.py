from pytest_mock import MockerFixture
from unittest.mock import MagicMock, call as MockCall

from ahriman.core.spawn import Spawn


def test_boolean_action_argument() -> None:
    """
    must correctly convert argument to boolean flag
    """
    assert Spawn.boolean_action_argument("option", True) == "option"
    assert Spawn.boolean_action_argument("option", False) == "no-option"


def test_process(spawner: Spawn) -> None:
    """
    must process external process run correctly
    """
    args = MagicMock()
    callback = MagicMock()
    callback.return_value = True

    spawner.process(callback, args, spawner.architecture, "id", spawner.queue)

    callback.assert_called_once_with(args, spawner.architecture)
    (uuid, status, time) = spawner.queue.get()
    assert uuid == "id"
    assert status
    assert time >= 0
    assert spawner.queue.empty()


def test_process_error(spawner: Spawn) -> None:
    """
    must process external run with error correctly
    """
    callback = MagicMock()
    callback.return_value = False

    spawner.process(callback, MagicMock(), spawner.architecture, "id", spawner.queue)

    (uuid, status, time) = spawner.queue.get()
    assert uuid == "id"
    assert not status
    assert time >= 0
    assert spawner.queue.empty()


def test_spawn_process(spawner: Spawn, mocker: MockerFixture) -> None:
    """
    must correctly spawn child process
    """
    start_mock = mocker.patch("multiprocessing.Process.start")

    assert spawner._spawn_process("add", "ahriman", now="", maybe="?", none=None)
    start_mock.assert_called_once_with()
    spawner.args_parser.parse_args.assert_called_once_with(
        spawner.command_arguments + [
            "add", "ahriman", "--now", "--maybe", "?"
        ]
    )


def test_has_process(spawner: Spawn) -> None:
    """
    must correctly determine if there is a process
    """
    assert not spawner.has_process("id")

    spawner.active["id"] = MagicMock()
    assert spawner.has_process("id")


def test_key_import(spawner: Spawn, mocker: MockerFixture) -> None:
    """
    must call key import
    """
    spawn_mock = mocker.patch("ahriman.core.spawn.Spawn._spawn_process")
    assert spawner.key_import("0xdeadbeaf", None)
    spawn_mock.assert_called_once_with("service-key-import", "0xdeadbeaf")


def test_key_import_with_server(spawner: Spawn, mocker: MockerFixture) -> None:
    """
    must call key import with server specified
    """
    spawn_mock = mocker.patch("ahriman.core.spawn.Spawn._spawn_process")
    assert spawner.key_import("0xdeadbeaf", "keyserver.ubuntu.com")
    spawn_mock.assert_called_once_with("service-key-import", "0xdeadbeaf", **{"key-server": "keyserver.ubuntu.com"})


def test_packages_add(spawner: Spawn, mocker: MockerFixture) -> None:
    """
    must call package addition
    """
    spawn_mock = mocker.patch("ahriman.core.spawn.Spawn._spawn_process")
    assert spawner.packages_add(["ahriman", "linux"], None, now=False)
    spawn_mock.assert_called_once_with("package-add", "ahriman", "linux", username=None)


def test_packages_add_with_build(spawner: Spawn, mocker: MockerFixture) -> None:
    """
    must call package addition with update
    """
    spawn_mock = mocker.patch("ahriman.core.spawn.Spawn._spawn_process")
    assert spawner.packages_add(["ahriman", "linux"], None, now=True)
    spawn_mock.assert_called_once_with("package-add", "ahriman", "linux", username=None, now="")


def test_packages_add_with_username(spawner: Spawn, mocker: MockerFixture) -> None:
    """
    must call package addition with username
    """
    spawn_mock = mocker.patch("ahriman.core.spawn.Spawn._spawn_process")
    assert spawner.packages_add(["ahriman", "linux"], "username", now=False)
    spawn_mock.assert_called_once_with("package-add", "ahriman", "linux", username="username")


def test_packages_rebuild(spawner: Spawn, mocker: MockerFixture) -> None:
    """
    must call package rebuild
    """
    spawn_mock = mocker.patch("ahriman.core.spawn.Spawn._spawn_process")
    assert spawner.packages_rebuild("python", "packager")
    spawn_mock.assert_called_once_with("repo-rebuild", **{"depends-on": "python", "username": "packager"})


def test_packages_remove(spawner: Spawn, mocker: MockerFixture) -> None:
    """
    must call package removal
    """
    spawn_mock = mocker.patch("ahriman.core.spawn.Spawn._spawn_process")
    assert spawner.packages_remove(["ahriman", "linux"])
    spawn_mock.assert_called_once_with("package-remove", "ahriman", "linux")


def test_packages_update(spawner: Spawn, mocker: MockerFixture) -> None:
    """
    must call repo update
    """
    spawn_mock = mocker.patch("ahriman.core.spawn.Spawn._spawn_process")

    assert spawner.packages_update("packager", aur=True, local=True, manual=True)
    args = {"username": "packager", "aur": "", "local": "", "manual": ""}
    spawn_mock.assert_called_once_with("repo-update", **args)
    spawn_mock.reset_mock()

    assert spawner.packages_update("packager", aur=False, local=True, manual=True)
    args = {"username": "packager", "no-aur": "", "local": "", "manual": ""}
    spawn_mock.assert_called_once_with("repo-update", **args)
    spawn_mock.reset_mock()

    assert spawner.packages_update("packager", aur=True, local=False, manual=True)
    args = {"username": "packager", "aur": "", "no-local": "", "manual": ""}
    spawn_mock.assert_called_once_with("repo-update", **args)
    spawn_mock.reset_mock()

    assert spawner.packages_update("packager", aur=True, local=True, manual=False)
    args = {"username": "packager", "aur": "", "local": "", "no-manual": ""}
    spawn_mock.assert_called_once_with("repo-update", **args)
    spawn_mock.reset_mock()


def test_run(spawner: Spawn, mocker: MockerFixture) -> None:
    """
    must implement run method
    """
    logging_mock = mocker.patch("logging.Logger.info")

    spawner.queue.put(("1", False, 1))
    spawner.queue.put(("2", True, 1))
    spawner.queue.put(None)  # terminate

    spawner.run()
    logging_mock.assert_called()


def test_run_pop(spawner: Spawn) -> None:
    """
    must pop and terminate child process
    """
    first = spawner.active["1"] = MagicMock()
    second = spawner.active["2"] = MagicMock()

    spawner.queue.put(("1", False, 1))
    spawner.queue.put(("2", True, 1))
    spawner.queue.put(None)  # terminate

    spawner.run()

    first.join.assert_called_once_with()
    second.join.assert_called_once_with()
    assert not spawner.active


def test_stop(spawner: Spawn) -> None:
    """
    must gracefully terminate thread
    """
    spawner.start()
    spawner.stop()
    spawner.join()

    assert not spawner.is_alive()
