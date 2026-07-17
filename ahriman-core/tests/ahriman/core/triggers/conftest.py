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
    _, repository_id = configuration.check_loaded()
    return Trigger(repository_id, configuration)


@pytest.fixture
def trigger_loader(configuration: Configuration) -> TriggerLoader:
    """
    fixture for trigger loader
    Args:
        configuration(Configuration): configuration fixture

    Returns:
        TriggerLoader: trigger loader test instance
    """
    _, repository_id = configuration.check_loaded()
    return TriggerLoader.load(repository_id, configuration)
