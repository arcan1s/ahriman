import pytest

from ahriman.core.configuration import Configuration
from ahriman.core.status.client import Client
from ahriman.core.status.web_client import WebClient


# fixtures
@pytest.fixture
def client() -> Client:
    """
    fixture for dummy client
    :return: dummy client test instance
    """
    return Client()


@pytest.fixture
def web_client(configuration: Configuration) -> WebClient:
    """
    fixture for web client
    :param configuration: configuration fixture
    :return: web client test instance
    """
    configuration.set("web", "port", "8080")
    return WebClient(configuration)
