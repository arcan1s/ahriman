import time

from ahriman.core.distributed import WorkersCache
from ahriman.models.worker import Worker


def test_workers(workers_cache: WorkersCache) -> None:
    """
    must return alive workers
    """
    workers_cache._workers = {
        str(index): (Worker(f"address{index}"), index)
        for index in range(2)
    }
    workers_cache.time_to_live = time.monotonic()

    assert workers_cache.workers == [Worker("address1")]


def test_workers_remove(workers_cache: WorkersCache) -> None:
    """
    must remove all workers
    """
    workers_cache.workers_update(Worker("address"))
    assert workers_cache.workers

    workers_cache.workers_remove()
    assert not workers_cache.workers


def test_workers_update(workers_cache: WorkersCache) -> None:
    """
    must update worker
    """
    worker = Worker("address")

    workers_cache.workers_update(worker)
    assert workers_cache.workers == [worker]
    _, first_last_seen = workers_cache._workers[worker.identifier]

    workers_cache.workers_update(worker)
    _, second_last_seen = workers_cache._workers[worker.identifier]
    assert first_last_seen < second_last_seen
