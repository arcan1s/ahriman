import json
import requests

from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.distributed.distributed_system import DistributedSystem
from ahriman.models.worker import Worker


def test_identifier_path(configuration: Configuration) -> None:
    """
    must correctly set default identifier path
    """
    configuration.set_option("status", "address", "http://localhost:8081")
    _, repository_id = configuration.check_loaded()
    assert DistributedSystem(repository_id, configuration).identifier_path


def test_configuration_sections(configuration: Configuration) -> None:
    """
    must correctly parse target list
    """
    assert DistributedSystem.configuration_sections(configuration) == ["worker"]


def test_workers_url(distributed_system: DistributedSystem) -> None:
    """
    must generate workers url correctly
    """
    assert distributed_system._workers_url().startswith(distributed_system.address)
    assert distributed_system._workers_url().endswith("/api/v1/distributed")

    assert distributed_system._workers_url("id").startswith(distributed_system.address)
    assert distributed_system._workers_url("id").endswith("/api/v1/distributed/id")


def test_load_identifier(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must generate identifier
    """
    mocker.patch("pathlib.Path.is_file", return_value=False)
    configuration.set_option("status", "address", "http://localhost:8081")
    _, repository_id = configuration.check_loaded()
    system = DistributedSystem(repository_id, configuration)

    assert system.load_identifier(configuration, "worker")


def test_load_identifier_configuration(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must load identifier from configuration
    """
    identifier = "id"
    mocker.patch("pathlib.Path.is_file", return_value=False)
    configuration.set_option("worker", "identifier", identifier)
    configuration.set_option("status", "address", "http://localhost:8081")
    _, repository_id = configuration.check_loaded()
    system = DistributedSystem(repository_id, configuration)

    assert system.worker.identifier == identifier


def test_load_identifier_filesystem(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must load identifier from filesystem
    """
    identifier = "id"
    mocker.patch("pathlib.Path.is_file", return_value=True)
    read_mock = mocker.patch("pathlib.Path.read_text", return_value=identifier)
    configuration.set_option("status", "address", "http://localhost:8081")
    _, repository_id = configuration.check_loaded()
    system = DistributedSystem(repository_id, configuration)

    assert system.worker.identifier == identifier
    read_mock.assert_called_once_with(encoding="utf8")


def test_register(distributed_system: DistributedSystem, mocker: MockerFixture) -> None:
    """
    must register service
    """
    mocker.patch("pathlib.Path.is_file", return_value=False)
    run_mock = mocker.patch("ahriman.core.distributed.distributed_system.DistributedSystem.make_request")
    write_mock = mocker.patch("pathlib.Path.write_text")

    distributed_system.register()
    run_mock.assert_called_once_with("POST", f"{distributed_system.address}/api/v1/distributed",
                                     json=distributed_system.worker.view())
    write_mock.assert_called_once_with(distributed_system.worker.identifier, encoding="utf8")
    assert distributed_system._owe_identifier


def test_register_skip(distributed_system: DistributedSystem, mocker: MockerFixture) -> None:
    """
    must skip service registration if it doesn't owe the identifier
    """
    mocker.patch("pathlib.Path.is_file", return_value=True)
    run_mock = mocker.patch("ahriman.core.distributed.distributed_system.DistributedSystem.make_request")
    write_mock = mocker.patch("pathlib.Path.write_text")

    distributed_system.register()
    run_mock.assert_not_called()
    write_mock.assert_not_called()
    assert not distributed_system._owe_identifier


def test_register_force(distributed_system: DistributedSystem, mocker: MockerFixture) -> None:
    """
    must register service even if it doesn't owe the identifier if force is supplied
    """
    mocker.patch("pathlib.Path.is_file", return_value=True)
    run_mock = mocker.patch("ahriman.core.distributed.distributed_system.DistributedSystem.make_request")
    write_mock = mocker.patch("pathlib.Path.write_text")

    distributed_system.register(force=True)
    run_mock.assert_called_once_with("POST", f"{distributed_system.address}/api/v1/distributed",
                                     json=distributed_system.worker.view())
    write_mock.assert_called_once_with(distributed_system.worker.identifier, encoding="utf8")
    assert distributed_system._owe_identifier


def test_unregister(distributed_system: DistributedSystem, mocker: MockerFixture) -> None:
    """
    must unregister service
    """
    run_mock = mocker.patch("ahriman.core.distributed.distributed_system.DistributedSystem.make_request")
    remove_mock = mocker.patch("pathlib.Path.unlink")
    distributed_system._owe_identifier = True

    distributed_system.unregister()
    run_mock.assert_called_once_with(
        "DELETE", f"{distributed_system.address}/api/v1/distributed/{distributed_system.worker.identifier}")
    remove_mock.assert_called_once_with(missing_ok=True)


def test_unregister_skip(distributed_system: DistributedSystem, mocker: MockerFixture) -> None:
    """
    must skip service removal if it doesn't owe the identifier
    """
    run_mock = mocker.patch("ahriman.core.distributed.distributed_system.DistributedSystem.make_request")
    remove_mock = mocker.patch("pathlib.Path.unlink")

    distributed_system.unregister()
    run_mock.assert_not_called()
    remove_mock.assert_not_called()


def test_unregister_force(distributed_system: DistributedSystem, mocker: MockerFixture) -> None:
    """
    must remove service even if it doesn't owe the identifier if force is supplied
    """
    run_mock = mocker.patch("ahriman.core.distributed.distributed_system.DistributedSystem.make_request")
    remove_mock = mocker.patch("pathlib.Path.unlink")

    distributed_system.unregister(force=True)
    run_mock.assert_called_once_with(
        "DELETE", f"{distributed_system.address}/api/v1/distributed/{distributed_system.worker.identifier}")
    remove_mock.assert_called_once_with(missing_ok=True)


def test_workers_get(distributed_system: DistributedSystem, mocker: MockerFixture) -> None:
    """
    must return available remote workers
    """
    worker = Worker("remote")
    response_obj = requests.Response()
    response_obj._content = json.dumps([worker.view()]).encode("utf8")
    response_obj.status_code = 200

    requests_mock = mocker.patch("ahriman.core.status.web_client.WebClient.make_request",
                                 return_value=response_obj)

    result = distributed_system.workers()
    requests_mock.assert_called_once_with("GET", distributed_system._workers_url())
    assert result == [worker]
