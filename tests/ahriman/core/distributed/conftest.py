import pytest

from ahriman.core.configuration import Configuration
from ahriman.core.distributed import WorkerTrigger, WorkersCache
from ahriman.core.distributed.distributed_system import DistributedSystem


@pytest.fixture
def distributed_system(configuration: Configuration) -> DistributedSystem:
    """
    distributed system fixture

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        DistributedSystem: distributed system test instance
    """
    configuration.set_option("status", "address", "http://localhost:8081")
    _, repository_id = configuration.check_loaded()
    return DistributedSystem(repository_id, configuration)


@pytest.fixture
def worker_trigger(configuration: Configuration) -> WorkerTrigger:
    """
    worker trigger fixture

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        WorkerTrigger: worker trigger test instance
    """
    configuration.set_option("status", "address", "http://localhost:8081")
    _, repository_id = configuration.check_loaded()
    return WorkerTrigger(repository_id, configuration)


@pytest.fixture
def workers_cache(configuration: Configuration) -> WorkersCache:
    """
    workers cache fixture

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        WorkersCache: workers cache test instance
    """
    return WorkersCache(configuration)
