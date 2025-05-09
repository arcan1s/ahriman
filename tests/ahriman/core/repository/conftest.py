import pytest

from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.repository.cleaner import Cleaner
from ahriman.core.repository.executor import Executor
from ahriman.core.repository.package_info import PackageInfo
from ahriman.core.repository.update_handler import UpdateHandler
from ahriman.models.pacman_synchronization import PacmanSynchronization


@pytest.fixture
def cleaner(configuration: Configuration, database: SQLite) -> Cleaner:
    """
    fixture for cleaner

    Args:
        configuration(Configuration): configuration fixture
        database(SQLite): database fixture

    Returns:
        Cleaner: cleaner test instance
    """
    _, repository_id = configuration.check_loaded()
    return Cleaner(repository_id, configuration, database, report=False,
                   refresh_pacman_database=PacmanSynchronization.Disabled)


@pytest.fixture
def executor(configuration: Configuration, database: SQLite, mocker: MockerFixture) -> Executor:
    """
    fixture for executor

    Args:
        configuration(Configuration): configuration fixture
        database(SQLite): database fixture
        mocker(MockerFixture): mocker object

    Returns:
        Executor: executor test instance
    """
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_cache")
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_chroot")
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_packages")
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_queue")
    _, repository_id = configuration.check_loaded()
    return Executor(repository_id, configuration, database, report=False,
                    refresh_pacman_database=PacmanSynchronization.Disabled)


@pytest.fixture
def package_info(configuration: Configuration, database: SQLite) -> PackageInfo:
    """
    fixture for package info

    Args:
        configuration(Configuration): configuration fixture
        database(SQLite): database fixture

    Returns:
        PackageInfo: package info test instance
    """
    _, repository_id = configuration.check_loaded()
    return PackageInfo(repository_id, configuration, database, report=False,
                       refresh_pacman_database=PacmanSynchronization.Disabled)


@pytest.fixture
def update_handler(configuration: Configuration, database: SQLite, mocker: MockerFixture) -> UpdateHandler:
    """
    fixture for update handler

    Args:
        configuration(Configuration): configuration fixture
        database(SQLite): database fixture
        mocker(MockerFixture): mocker object

    Returns:
        UpdateHandler: update handler test instance
    """
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_cache")
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_chroot")
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_packages")
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_queue")
    _, repository_id = configuration.check_loaded()
    return UpdateHandler(repository_id, configuration, database, report=False,
                         refresh_pacman_database=PacmanSynchronization.Disabled)
