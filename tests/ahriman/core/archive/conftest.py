import pytest

from ahriman.core.archive import ArchiveTrigger
from ahriman.core.archive.archive_tree import ArchiveTree
from ahriman.core.configuration import Configuration


@pytest.fixture
def archive_tree(configuration: Configuration) -> ArchiveTree:
    """
    archive tree fixture

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        ArchiveTree: archive tree test instance
    """
    return ArchiveTree(configuration.repository_paths, [])


@pytest.fixture
def archive_trigger(configuration: Configuration) -> ArchiveTrigger:
    """
    archive trigger fixture

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        ArchiveTrigger: archive trigger test instance
    """
    _, repository_id = configuration.check_loaded()
    return ArchiveTrigger(repository_id, configuration)
