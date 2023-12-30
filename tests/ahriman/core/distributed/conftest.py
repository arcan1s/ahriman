import pytest

from ahriman.core.configuration import Configuration
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
