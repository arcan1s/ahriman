import pytest

from ahriman.core.configuration import Configuration
from ahriman.core.status import Client
from ahriman.core.status.event_bus import EventBus
from ahriman.core.status.web_client import WebClient


@pytest.fixture
def client() -> Client:
    """
    fixture for dummy client

    Returns:
        Client: dummy client test instance
    """
    return Client()


@pytest.fixture
def event_bus() -> EventBus:
    """
    fixture for event bus

    Returns:
        EventBus: event bus test instance
    """
    return EventBus(0)


@pytest.fixture
def web_client(configuration: Configuration) -> WebClient:
    """
    fixture for web client

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        WebClient: web client test instance
    """
    configuration.set("web", "port", "8080")
    _, repository_id = configuration.check_loaded()
    return WebClient(repository_id, configuration)
