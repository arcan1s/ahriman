import pytest

from ahriman.core.auth.mapping import Mapping
from ahriman.core.configuration import Configuration


@pytest.fixture
def mapping_auth(configuration: Configuration) -> Mapping:
    """
    auth provider fixture
    :return: auth service instance
    """
    return Mapping(configuration)
