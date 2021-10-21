import pytest

from pytest_mock import MockerFixture

from ahriman.application.application.packages import Packages
from ahriman.application.application.properties import Properties
from ahriman.application.application.repository import Repository
from ahriman.core.configuration import Configuration


@pytest.fixture
def application_packages(configuration: Configuration, mocker: MockerFixture) -> Packages:
    """
    fixture for application with package functions
    :param configuration: configuration fixture
    :param mocker: mocker object
    :return: application test instance
    """
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    return Packages("x86_64", configuration, no_report=True)


@pytest.fixture
def application_properties(configuration: Configuration, mocker: MockerFixture) -> Properties:
    """
    fixture for application with properties only
    :param configuration: configuration fixture
    :param mocker: mocker object
    :return: application test instance
    """
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    return Properties("x86_64", configuration, no_report=True)


@pytest.fixture
def application_repository(configuration: Configuration, mocker: MockerFixture) -> Repository:
    """
    fixture for application with repository functions
    :param configuration: configuration fixture
    :param mocker: mocker object
    :return: application test instance
    """
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    return Repository("x86_64", configuration, no_report=True)
