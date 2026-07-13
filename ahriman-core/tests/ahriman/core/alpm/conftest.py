import pytest

from ahriman.core.alpm.pacman_database import PacmanDatabase
from ahriman.core.alpm.pacman import Pacman
from ahriman.core.configuration import Configuration


@pytest.fixture
def pacman_database(configuration: Configuration, pacman: Pacman) -> PacmanDatabase:
    """
    database sync fixture

    Args:
        configuration(Configuration): configuration test instance
        pacman(Pacman): pacman test instance

    Returns:
        DatabaseSync: database sync test instance
    """
    database = next(iter(pacman.handle.get_syncdbs()))
    return PacmanDatabase(database, configuration)
