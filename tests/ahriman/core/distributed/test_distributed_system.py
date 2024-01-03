import json
import requests

from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.distributed.distributed_system import DistributedSystem
from ahriman.models.worker import Worker


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


def test_register(distributed_system: DistributedSystem, mocker: MockerFixture) -> None:
    """
    must register service
    """
    run_mock = mocker.patch("ahriman.core.distributed.distributed_system.DistributedSystem.make_request")
    distributed_system.register()
    run_mock.assert_called_once_with("POST", f"{distributed_system.address}/api/v1/distributed",
                                     json=distributed_system.worker.view())


def test_register_failed(distributed_system: DistributedSystem, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during worker registration
    """
    mocker.patch("requests.Session.request", side_effect=Exception())
    distributed_system.register()


def test_register_failed_http_error(distributed_system: DistributedSystem, mocker: MockerFixture) -> None:
    """
    must suppress HTTP exception happened during worker registration
    """
    mocker.patch("requests.Session.request", side_effect=requests.HTTPError())
    distributed_system.register()


def test_workers(distributed_system: DistributedSystem, mocker: MockerFixture) -> None:
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


def test_workers_failed(distributed_system: DistributedSystem, mocker: MockerFixture) -> None:
    """
    must suppress any exception happened during worker extraction
    """
    mocker.patch("requests.Session.request", side_effect=Exception())
    distributed_system.workers()


def test_workers_failed_http_error(distributed_system: DistributedSystem, mocker: MockerFixture) -> None:
    """
    must suppress HTTP exception happened during worker extraction
    """
    mocker.patch("requests.Session.request", side_effect=requests.HTTPError())
    distributed_system.workers()
