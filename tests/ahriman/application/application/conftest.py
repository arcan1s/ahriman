import pytest

from pytest_mock import MockerFixture

from ahriman.application.application.application_packages import ApplicationPackages
from ahriman.application.application.application_properties import ApplicationProperties
from ahriman.application.application.application_repository import ApplicationRepository
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite


@pytest.fixture
def application_packages(configuration: Configuration, database: SQLite, mocker: MockerFixture) -> ApplicationPackages:
    """
    fixture for application with package functions

    Args:
        configuration(Configuration): configuration fixture
        database(SQLite): database fixture
        mocker(MockerFixture): mocker object

    Returns:
        ApplicationPackages: application test instance
    """
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    mocker.patch("ahriman.core.database.SQLite.load", return_value=database)
    return ApplicationPackages("x86_64", configuration, report=False, unsafe=False)


@pytest.fixture
def application_properties(configuration: Configuration, database: SQLite,
                           mocker: MockerFixture) -> ApplicationProperties:
    """
    fixture for application with properties only

    Args:
        configuration(Configuration): configuration fixture
        database(SQLite): database fixture
        mocker(MockerFixture): mocker object

    Returns:
        ApplicationProperties: application test instance
    """
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    mocker.patch("ahriman.core.database.SQLite.load", return_value=database)
    return ApplicationProperties("x86_64", configuration, report=False, unsafe=False)


@pytest.fixture
def application_repository(configuration: Configuration, database: SQLite,
                           mocker: MockerFixture) -> ApplicationRepository:
    """
    fixture for application with repository functions

    Args:
        configuration(Configuration): configuration fixture
        database(SQLite): database fixture
        mocker(MockerFixture): mocker object

    Returns:
        ApplicationRepository: application test instance
    """
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    mocker.patch("ahriman.core.database.SQLite.load", return_value=database)
    return ApplicationRepository("x86_64", configuration, report=False, unsafe=False)
