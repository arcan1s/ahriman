import pytest

from ahriman.core.configuration import Configuration
from ahriman.core.report.remote_call import RemoteCall


@pytest.fixture
def remote_call(configuration: Configuration) -> RemoteCall:
    """
    fixture for remote update trigger

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        RemoteCall: remote update trigger test instance
    """
    configuration.set_option("web", "host", "localhost")
    configuration.set_option("web", "port", "8080")
    return RemoteCall("x86_64", configuration, "remote-call")