import pytest

from pytest_mock import MockerFixture

from ahriman.application.application.packages import Packages
from ahriman.application.application.properties import Properties
from ahriman.application.application.repository import Repository
from ahriman.core.configuration import Configuration
from ahriman.core.database.sqlite import SQLite


@pytest.fixture
def application_packages(configuration: Configuration, database: SQLite, mocker: MockerFixture) -> Packages:
    """
    fixture for application with package functions

    Args:
        configuration(Configuration): configuration fixture
        database(SQLite): database fixture
        mocker(MockerFixture): mocker object

    Returns:
        Packages: application test instance
    """
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    mocker.patch("ahriman.core.database.sqlite.SQLite.load", return_value=database)
    return Packages("x86_64", configuration, no_report=True, unsafe=False)


@pytest.fixture
def application_properties(configuration: Configuration, database: SQLite, mocker: MockerFixture) -> Properties:
    """
    fixture for application with properties only

    Args:
        configuration(Configuration): configuration fixture
        database(SQLite): database fixture
        mocker(MockerFixture): mocker object

    Returns:
        Properties: application test instance
    """
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    mocker.patch("ahriman.core.database.sqlite.SQLite.load", return_value=database)
    return Properties("x86_64", configuration, no_report=True, unsafe=False)


@pytest.fixture
def application_repository(configuration: Configuration, database: SQLite, mocker: MockerFixture) -> Repository:
    """
    fixture for application with repository functions

    Args:
        configuration(Configuration): configuration fixture
        database(SQLite): database fixture
        mocker(MockerFixture): mocker object

    Returns:
        Repository: application test instance
    """
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    mocker.patch("ahriman.core.database.sqlite.SQLite.load", return_value=database)
    return Repository("x86_64", configuration, no_report=True, unsafe=False)
