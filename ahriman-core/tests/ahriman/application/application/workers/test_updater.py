import pytest

from ahriman.application.application.workers import Updater
from ahriman.application.application.workers.local_updater import LocalUpdater
from ahriman.application.application.workers.remote_updater import RemoteUpdater
from ahriman.core.configuration import Configuration
from ahriman.core.repository import Repository
from ahriman.models.worker import Worker


def test_load(configuration: Configuration, repository: Repository) -> None:
    """
    must load local updater if empty worker list is set
    """
    _, repository_id = configuration.check_loaded()
    assert isinstance(Updater.load(repository_id, configuration, repository), LocalUpdater)
    assert isinstance(Updater.load(repository_id, configuration, repository, []), LocalUpdater)


def test_load_from_option(configuration: Configuration, repository: Repository) -> None:
    """
    must load remote updater if nonempty worker list is set
    """
    _, repository_id = configuration.check_loaded()
    assert isinstance(Updater.load(repository_id, configuration, repository, [Worker("remote")]), RemoteUpdater)


def test_load_from_configuration(configuration: Configuration, repository: Repository) -> None:
    """
    must load remote updater from settings
    """
    configuration.set_option("build", "workers", "remote")
    _, repository_id = configuration.check_loaded()
    assert isinstance(Updater.load(repository_id, configuration, repository), RemoteUpdater)


def test_partition(updater: Updater) -> None:
    """
    must raise not implemented error for missing partition method
    """
    with pytest.raises(NotImplementedError):
        updater.partition([])


def test_update(updater: Updater) -> None:
    """
    must raise not implemented error for missing update method
    """
    with pytest.raises(NotImplementedError):
        updater.update([])
