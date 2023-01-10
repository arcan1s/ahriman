import pytest

from ahriman.core.configuration import Configuration
from ahriman.core.triggers import Trigger, TriggerLoader


@pytest.fixture
def trigger(configuration: Configuration) -> Trigger:
    """
    fixture for trigger

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        Trigger: trigger test instance
    """
    return Trigger("x86_64", configuration)


@pytest.fixture
def trigger_loader(configuration: Configuration) -> TriggerLoader:
    """
    fixture for trigger loader
    Args:
        configuration(Configuration): configuration fixture

    Returns:
        TriggerLoader: trigger loader test instance
    """
    return TriggerLoader.load("x86_64", configuration)
