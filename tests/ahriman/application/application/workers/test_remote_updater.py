from pytest_mock import MockerFixture

from ahriman.application.application.workers.remote_updater import RemoteUpdater
from ahriman.core.http import SyncAhrimanClient
from ahriman.models.package import Package
from ahriman.models.packagers import Packagers
from ahriman.models.result import Result


def test_clients(remote_updater: RemoteUpdater) -> None:
    """
    must return map of clients
    """
    worker = remote_updater.workers[0]
    client = SyncAhrimanClient()
    remote_updater._clients.append((worker, client))

    assert remote_updater.clients == {worker: client}


def test_update_url(remote_updater: RemoteUpdater) -> None:
    """
    must generate update url correctly
    """
    worker = remote_updater.workers[0]
    assert remote_updater._update_url(worker).startswith(worker.address)
    assert remote_updater._update_url(worker).endswith("/api/v1/service/add")


def test_next_worker(remote_updater: RemoteUpdater) -> None:
    """
    must return next not used worker
    """
    assert remote_updater.next_worker()[0] == remote_updater.workers[0]
    assert len(remote_updater.clients) == 1
    assert remote_updater.workers[0] in remote_updater.clients

    assert remote_updater.next_worker()[0] == remote_updater.workers[1]
    assert remote_updater.workers[1] in remote_updater.clients
    assert len(remote_updater.clients) == 2


def test_next_worker_cycle(remote_updater: RemoteUpdater) -> None:
    """
    must return first used worker if no free workers left
    """
    worker1, client1 = remote_updater.next_worker()
    worker2, client2 = remote_updater.next_worker()

    assert remote_updater.next_worker() == (worker1, client1)
    assert remote_updater.next_worker() == (worker2, client2)
    assert remote_updater.next_worker() == (worker1, client1)


def test_partition(remote_updater: RemoteUpdater, mocker: MockerFixture) -> None:
    """
    must partition as tree partition
    """
    resolve_mock = mocker.patch("ahriman.core.tree.Tree.partition")
    remote_updater.partition([])
    resolve_mock.assert_called_once_with([], count=2)


def test_update(remote_updater: RemoteUpdater, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must process remote package updates
    """
    worker, client = remote_updater.next_worker()
    worker_mock = mocker.patch("ahriman.application.application.workers.remote_updater.RemoteUpdater.next_worker",
                               return_value=(worker, client))
    request_mock = mocker.patch("ahriman.core.http.SyncAhrimanClient.make_request")

    assert remote_updater.update([package_ahriman], Packagers("username"), bump_pkgrel=True) == Result()
    worker_mock.assert_called_once_with()
    request_mock.assert_called_once_with("POST", remote_updater._update_url(worker),
                                         params=remote_updater.repository_id.query(),
                                         json={
                                             "increment": True,
                                             "packager": "username",
                                             "packages": [package_ahriman.base],
                                             "patches": [],
                                             "refresh": True,
    }
    )
