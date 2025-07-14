import pytest

from ahriman.core.configuration import Configuration
from ahriman.core.housekeeping import LogsRotationTrigger


@pytest.fixture
def logs_rotation_trigger(configuration: Configuration) -> LogsRotationTrigger:
    """
    logs roration trigger fixture

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        LogsRotationTrigger: logs rotation trigger test instance
    """
    _, repository_id = configuration.check_loaded()
    return LogsRotationTrigger(repository_id, configuration)
