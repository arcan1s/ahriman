import pytest

from ahriman.core.configuration import Configuration
from ahriman.core.housekeeping import ArchiveRotationTrigger, EventsRotationTrigger, LogsRotationTrigger


@pytest.fixture
def archive_rotation_trigger(configuration: Configuration) -> ArchiveRotationTrigger:
    """
    archive rotation trigger fixture

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        ArchiveRotationTrigger: archive rotation trigger test instance
    """
    _, repository_id = configuration.check_loaded()
    return ArchiveRotationTrigger(repository_id, configuration)


@pytest.fixture
def events_rotation_trigger(configuration: Configuration) -> EventsRotationTrigger:
    """
    events rotation trigger fixture

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        EventsRotationTrigger: events rotation trigger test instance
    """
    configuration.set_option("events-rotation", "keep_last_events", "1000")
    _, repository_id = configuration.check_loaded()
    return EventsRotationTrigger(repository_id, configuration)


@pytest.fixture
def logs_rotation_trigger(configuration: Configuration) -> LogsRotationTrigger:
    """
    logs rotation trigger fixture

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        LogsRotationTrigger: logs rotation trigger test instance
    """
    _, repository_id = configuration.check_loaded()
    return LogsRotationTrigger(repository_id, configuration)
