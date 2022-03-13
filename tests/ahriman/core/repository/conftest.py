import pytest

from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.repository import Repository
from ahriman.core.repository.cleaner import Cleaner
from ahriman.core.repository.executor import Executor
from ahriman.core.repository.properties import Properties
from ahriman.core.repository.update_handler import UpdateHandler


@pytest.fixture
def cleaner(configuration: Configuration, mocker: MockerFixture) -> Cleaner:
    """
    fixture for cleaner
    :param configuration: configuration fixture
    :param mocker: mocker object
    :return: cleaner test instance
    """
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    return Cleaner("x86_64", configuration, no_report=True, unsafe=False)


@pytest.fixture
def executor(configuration: Configuration, mocker: MockerFixture) -> Executor:
    """
    fixture for executor
    :param configuration: configuration fixture
    :param mocker: mocker object
    :return: executor test instance
    """
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_build")
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_cache")
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_chroot")
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_manual")
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_packages")
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    return Executor("x86_64", configuration, no_report=True, unsafe=False)


@pytest.fixture
def repository(configuration: Configuration, mocker: MockerFixture) -> Repository:
    """
    fixture for repository
    :param configuration: configuration fixture
    :param mocker: mocker object
    :return: repository test instance
    """
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    return Repository("x86_64", configuration, no_report=True, unsafe=False)


@pytest.fixture
def properties(configuration: Configuration) -> Properties:
    """
    fixture for properties
    :param configuration: configuration fixture
    :return: properties test instance
    """
    return Properties("x86_64", configuration, no_report=True, unsafe=False)


@pytest.fixture
def update_handler(configuration: Configuration, mocker: MockerFixture) -> UpdateHandler:
    """
    fixture for update handler
    :param configuration: configuration fixture
    :param mocker: mocker object
    :return: update handler test instance
    """
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_build")
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_cache")
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_chroot")
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_manual")
    mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_packages")
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    return UpdateHandler("x86_64", configuration, no_report=True, unsafe=False)
