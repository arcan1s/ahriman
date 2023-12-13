import pytest

from ahriman.application.application.workers import Updater
from ahriman.application.application.workers.local_updater import LocalUpdater
from ahriman.application.application.workers.remote_updater import RemoteUpdater
from ahriman.core.configuration import Configuration
from ahriman.core.repository import Repository
from ahriman.models.worker import Worker


@pytest.fixture
def local_updater(repository: Repository) -> LocalUpdater:
    """
    local updater fixture

    Args:
        repository(Repository): repository fixture

    Returns:
        LocalUpdater: local updater test instance
    """
    return LocalUpdater(repository)


@pytest.fixture
def remote_updater(configuration: Configuration) -> RemoteUpdater:
    """
    local updater fixture

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        RemoteUpdater: remote updater test instance
    """
    _, repository_id = configuration.check_loaded()
    return RemoteUpdater([Worker("remote1"), Worker("remote2")], repository_id, configuration)


@pytest.fixture
def updater() -> Updater:
    """
    empty updater fixture

    Returns:
        Updater: empty updater test instance
    """
    return Updater()
