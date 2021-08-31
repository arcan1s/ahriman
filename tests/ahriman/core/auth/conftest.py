import pytest

from ahriman.core.auth.mapping_auth import MappingAuth
from ahriman.core.configuration import Configuration


@pytest.fixture
def mapping_auth(configuration: Configuration) -> MappingAuth:
    """
    auth provider fixture
    :return: auth service instance
    """
    configuration.set("web", "auth", "yes")
    return MappingAuth(configuration)
