import pytest

from pytest_mock import MockerFixture
from unittest.mock import MagicMock

from ahriman.core.spawn import Spawn
from ahriman.models.pkgbuild_patch import PkgbuildPatch
from ahriman.models.process_status import ProcessStatus
from ahriman.models.repository_id import RepositoryId


def test_boolean_action_argument() -> None:
    """
    must correctly convert argument to boolean flag
    """
    assert Spawn.boolean_action_argument("option", True) == "option"
    assert Spawn.boolean_action_argument("option", False) == "no-option"


def test_process(spawner: Spawn, repository_id: RepositoryId) -> None:
    """
    must process external process run correctly
    """
    args = MagicMock()
    callback = MagicMock()
    callback.return_value = True

    spawner.process(callback, args, repository_id, "id", spawner.queue)

    callback.assert_called_once_with(args, repository_id)
    status = spawner.queue.get()
    assert status.process_id == "id"
    assert status.status
    assert status.consumed_time >= 0
    assert spawner.queue.empty()


def test_process_error(spawner: Spawn, repository_id: RepositoryId) -> None:
    """
    must process external run with error correctly
    """
    callback = MagicMock()
    callback.return_value = False

    spawner.process(callback, MagicMock(), repository_id, "id", spawner.queue)

    status = spawner.queue.get()
    assert status.process_id == "id"
    assert not status.status
    assert status.consumed_time >= 0
    assert spawner.queue.empty()


def test_spawn_process(spawner: Spawn, repository_id: RepositoryId, mocker: MockerFixture) -> None:
    """
    must correctly spawn child process
    """
    start_mock = mocker.patch("multiprocessing.Process.start")

    assert spawner._spawn_process(repository_id, "command", "argument",
                                  empty="", string="v", list=["a", "b"], empty_list=[], none=None)
    start_mock.assert_called_once_with()
    spawner.args_parser.parse_args.assert_called_once_with(
        spawner.command_arguments + [
            "command", "argument", "--empty", "--string", "v", "--list", "a", "--list", "b",
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
    spawn_mock.assert_called_once_with(pytest.helpers.anyvar(int), "service-key-import", "0xdeadbeaf")


def test_key_import_with_server(spawner: Spawn, mocker: MockerFixture) -> None:
    """
    must call key import with server specified
    """
    spawn_mock = mocker.patch("ahriman.core.spawn.Spawn._spawn_process")
    assert spawner.key_import("0xdeadbeaf", "keyserver.ubuntu.com")
    spawn_mock.assert_called_once_with(pytest.helpers.anyvar(int), "service-key-import", "0xdeadbeaf",
                                       **{"key-server": "keyserver.ubuntu.com"})


def test_packages_add(spawner: Spawn, repository_id: RepositoryId, mocker: MockerFixture) -> None:
    """
    must call package addition
    """
    spawn_mock = mocker.patch("ahriman.core.spawn.Spawn._spawn_process")
    assert spawner.packages_add(repository_id, ["ahriman", "linux"], None,
                                patches=[], now=False, increment=False, refresh=False)
    spawn_mock.assert_called_once_with(repository_id, "package-add", "ahriman", "linux",
                                       **{"username": None, "variable": [], "no-increment": ""})


def test_packages_add_with_build(spawner: Spawn, repository_id: RepositoryId, mocker: MockerFixture) -> None:
    """
    must call package addition with update
    """
    spawn_mock = mocker.patch("ahriman.core.spawn.Spawn._spawn_process")
    assert spawner.packages_add(repository_id, ["ahriman", "linux"], None,
                                patches=[], now=True, increment=False, refresh=False)
    spawn_mock.assert_called_once_with(repository_id, "package-add", "ahriman", "linux",
                                       **{"username": None, "variable": [], "no-increment": "", "now": ""})


def test_packages_add_with_username(spawner: Spawn, repository_id: RepositoryId, mocker: MockerFixture) -> None:
    """
    must call package addition with username
    """
    spawn_mock = mocker.patch("ahriman.core.spawn.Spawn._spawn_process")
    assert spawner.packages_add(repository_id, ["ahriman", "linux"], "username",
                                patches=[], now=False, increment=False, refresh=False)
    spawn_mock.assert_called_once_with(repository_id, "package-add", "ahriman", "linux",
                                       **{"username": "username", "variable": [], "no-increment": ""})


def test_packages_add_with_patches(spawner: Spawn, repository_id: RepositoryId, mocker: MockerFixture) -> None:
    """
    must call package addition with patches
    """
    patches = [PkgbuildPatch("key", "value"), PkgbuildPatch("key", "value")]
    spawn_mock = mocker.patch("ahriman.core.spawn.Spawn._spawn_process")
    assert spawner.packages_add(repository_id, ["ahriman", "linux"], None,
                                patches=patches, now=False, increment=False, refresh=False)
    spawn_mock.assert_called_once_with(repository_id, "package-add", "ahriman", "linux",
                                       **{
                                           "username": None,
                                           "variable": [patch.serialize() for patch in patches],
                                           "no-increment": ""
                                       })


def test_packages_add_with_increment(spawner: Spawn, repository_id: RepositoryId, mocker: MockerFixture) -> None:
    """
    must call package addition with increment
    """
    spawn_mock = mocker.patch("ahriman.core.spawn.Spawn._spawn_process")
    assert spawner.packages_add(repository_id, ["ahriman", "linux"], None,
                                patches=[], now=False, increment=True, refresh=False)
    spawn_mock.assert_called_once_with(repository_id, "package-add", "ahriman", "linux",
                                       **{"username": None, "variable": [], "increment": ""})


def test_packages_add_with_refresh(spawner: Spawn, repository_id: RepositoryId, mocker: MockerFixture) -> None:
    """
    must call package addition with refresh
    """
    spawn_mock = mocker.patch("ahriman.core.spawn.Spawn._spawn_process")
    assert spawner.packages_add(repository_id, ["ahriman", "linux"], None,
                                patches=[], now=False, increment=False, refresh=True)
    spawn_mock.assert_called_once_with(repository_id, "package-add", "ahriman", "linux",
                                       **{"username": None, "variable": [], "no-increment": "", "refresh": ""})


def test_packages_rebuild(spawner: Spawn, repository_id: RepositoryId, mocker: MockerFixture) -> None:
    """
    must call package rebuild
    """
    spawn_mock = mocker.patch("ahriman.core.spawn.Spawn._spawn_process")
    assert spawner.packages_rebuild(repository_id, "python", "packager", increment=False)
    spawn_mock.assert_called_once_with(repository_id, "repo-rebuild",
                                       **{"depends-on": "python", "username": "packager", "no-increment": ""})


def test_packages_rebuild_with_increment(spawner: Spawn, repository_id: RepositoryId, mocker: MockerFixture) -> None:
    """
    must call package rebuild with increment
    """
    spawn_mock = mocker.patch("ahriman.core.spawn.Spawn._spawn_process")
    assert spawner.packages_rebuild(repository_id, "python", "packager", increment=True)
    spawn_mock.assert_called_once_with(repository_id, "repo-rebuild",
                                       **{"depends-on": "python", "username": "packager", "increment": ""})


def test_packages_remove(spawner: Spawn, repository_id: RepositoryId, mocker: MockerFixture) -> None:
    """
    must call package removal
    """
    spawn_mock = mocker.patch("ahriman.core.spawn.Spawn._spawn_process")
    assert spawner.packages_remove(repository_id, ["ahriman", "linux"])
    spawn_mock.assert_called_once_with(repository_id, "package-remove", "ahriman", "linux")


def test_packages_update(spawner: Spawn, repository_id: RepositoryId, mocker: MockerFixture) -> None:
    """
    must call repo update
    """
    spawn_mock = mocker.patch("ahriman.core.spawn.Spawn._spawn_process")

    assert spawner.packages_update(repository_id, "packager",
                                   aur=True, local=True, manual=True, increment=False, refresh=False)
    args = {"username": "packager", "aur": "", "local": "", "manual": "", "no-increment": ""}
    spawn_mock.assert_called_once_with(repository_id, "repo-update", **args)
    spawn_mock.reset_mock()

    assert spawner.packages_update(repository_id, "packager",
                                   aur=False, local=True, manual=True, increment=False, refresh=False)
    args = {"username": "packager", "no-aur": "", "local": "", "manual": "", "no-increment": ""}
    spawn_mock.assert_called_once_with(repository_id, "repo-update", **args)
    spawn_mock.reset_mock()

    assert spawner.packages_update(repository_id, "packager",
                                   aur=True, local=False, manual=True, increment=False, refresh=False)
    args = {"username": "packager", "aur": "", "no-local": "", "manual": "", "no-increment": ""}
    spawn_mock.assert_called_once_with(repository_id, "repo-update", **args)
    spawn_mock.reset_mock()

    assert spawner.packages_update(repository_id, "packager",
                                   aur=True, local=True, manual=False, increment=False, refresh=False)
    args = {"username": "packager", "aur": "", "local": "", "no-manual": "", "no-increment": ""}
    spawn_mock.assert_called_once_with(repository_id, "repo-update", **args)
    spawn_mock.reset_mock()


def test_packages_update_with_increment(spawner: Spawn, repository_id: RepositoryId, mocker: MockerFixture) -> None:
    """
    must call repo update with increment
    """
    spawn_mock = mocker.patch("ahriman.core.spawn.Spawn._spawn_process")
    assert spawner.packages_update(repository_id, None,
                                   aur=True, local=True, manual=True, increment=True, refresh=False)
    spawn_mock.assert_called_once_with(repository_id, "repo-update",
                                       **{"username": None, "aur": "", "local": "", "manual": "", "increment": ""})


def test_packages_update_with_refresh(spawner: Spawn, repository_id: RepositoryId, mocker: MockerFixture) -> None:
    """
    must call repo update with refresh
    """
    spawn_mock = mocker.patch("ahriman.core.spawn.Spawn._spawn_process")
    assert spawner.packages_update(repository_id, None,
                                   aur=True, local=True, manual=True, increment=False, refresh=True)
    spawn_mock.assert_called_once_with(repository_id, "repo-update",
                                       **{
                                           "username": None,
                                           "aur": "",
                                           "local": "",
                                           "manual": "",
                                           "no-increment": "",
                                           "refresh": "",
                                       }
                                       )


def test_run(spawner: Spawn, mocker: MockerFixture) -> None:
    """
    must implement run method
    """
    logging_mock = mocker.patch("logging.Logger.info")

    spawner.queue.put(ProcessStatus("1", False, 1))
    spawner.queue.put(ProcessStatus("2", True, 1))
    spawner.queue.put(None)  # terminate

    spawner.run()
    logging_mock.assert_called()


def test_run_pop(spawner: Spawn) -> None:
    """
    must pop and terminate child process
    """
    first = spawner.active["1"] = MagicMock()
    second = spawner.active["2"] = MagicMock()

    spawner.queue.put(ProcessStatus("1", False, 1))
    spawner.queue.put(ProcessStatus("2", True, 1))
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
