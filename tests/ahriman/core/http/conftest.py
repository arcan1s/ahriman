import pytest

from ahriman.core.configuration import Configuration
from ahriman.core.http import SyncAhrimanClient
from ahriman.core.status.web_client import WebClient


@pytest.fixture
def ahriman_client(configuration: Configuration) -> SyncAhrimanClient:
    """
    ahriman web client fixture

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        SyncAhrimanClient: ahriman web client test instance
    """
    configuration.set("web", "port", "8080")
    _, repository_id = configuration.check_loaded()
    return WebClient(repository_id, configuration)
