import pytest

from pytest_mock import MockerFixture

from ahriman.core.archive import ArchiveTrigger
from ahriman.core.archive.archive_tree import ArchiveTree
from ahriman.core.configuration import Configuration
from ahriman.core.sign.gpg import GPG


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
def archive_trigger(configuration: Configuration, gpg: GPG, mocker: MockerFixture) -> ArchiveTrigger:
    """
    archive trigger fixture

    Args:
        configuration(Configuration): configuration fixture
        gpg(GPG): GPG fixture
        mocker(MockerFixture): mocker object

    Returns:
        ArchiveTrigger: archive trigger test instance
    """
    mocker.patch("ahriman.core._Context.get", return_value=GPG)
    _, repository_id = configuration.check_loaded()
    return ArchiveTrigger(repository_id, configuration)
