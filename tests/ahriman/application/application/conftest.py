import pytest

from pytest_mock import MockerFixture

from ahriman.application.application.application_packages import ApplicationPackages
from ahriman.application.application.application_properties import ApplicationProperties
from ahriman.application.application.application_repository import ApplicationRepository
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.repository import Repository


@pytest.fixture
def application_packages(configuration: Configuration, database: SQLite, repository: Repository,
                         mocker: MockerFixture) -> ApplicationPackages:
    """
    fixture for application with package functions

    Args:
        configuration(Configuration): configuration fixture
        database(SQLite): database fixture
        repository(Repository): repository fixture
        mocker(MockerFixture): mocker object

    Returns:
        ApplicationPackages: application test instance
    """
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    mocker.patch("ahriman.core.database.SQLite.load", return_value=database)
    _, repository_id = configuration.check_loaded()
    return ApplicationPackages(repository_id, configuration, report=False)


@pytest.fixture
def application_properties(configuration: Configuration, database: SQLite, repository: Repository,
                           mocker: MockerFixture) -> ApplicationProperties:
    """
    fixture for application with properties only

    Args:
        configuration(Configuration): configuration fixture
        database(SQLite): database fixture
        repository(Repository): repository fixture
        mocker(MockerFixture): mocker object

    Returns:
        ApplicationProperties: application test instance
    """
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    mocker.patch("ahriman.core.database.SQLite.load", return_value=database)
    _, repository_id = configuration.check_loaded()
    return ApplicationProperties(repository_id, configuration, report=False)


@pytest.fixture
def application_repository(configuration: Configuration, database: SQLite, repository: Repository,
                           mocker: MockerFixture) -> ApplicationRepository:
    """
    fixture for application with repository functions

    Args:
        configuration(Configuration): configuration fixture
        database(SQLite): database fixture
        repository(Repository): repository fixture
        mocker(MockerFixture): mocker object

    Returns:
        ApplicationRepository: application test instance
    """
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    mocker.patch("ahriman.core.database.SQLite.load", return_value=database)
    _, repository_id = configuration.check_loaded()
    return ApplicationRepository(repository_id, configuration, report=False)
