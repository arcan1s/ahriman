import pytest

from ahriman.core.configuration import Configuration
from ahriman.core.configuration.schema import CONFIGURATION_SCHEMA
from ahriman.core.configuration.validator import Validator


@pytest.fixture
def validator(configuration: Configuration) -> Validator:
    """
    fixture for validator

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        Validator: validator test instance
    """
    return Validator(instance=configuration, schema=CONFIGURATION_SCHEMA)
