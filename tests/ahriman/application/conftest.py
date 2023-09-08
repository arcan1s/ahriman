import argparse
import pytest

from pytest_mock import MockerFixture

from ahriman.application.ahriman import _parser
from ahriman.application.application import Application
from ahriman.application.lock import Lock
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.repository import Repository


@pytest.fixture
def application(configuration: Configuration, repository: Repository, database: SQLite,
                mocker: MockerFixture) -> Application:
    """
    fixture for application

    Args:
        configuration(Configuration): configuration fixture
        database(SQLite): database fixture
        repository(Repository): repository fixture
        mocker(MockerFixture): mocker object

    Returns:
        Application: application test instance
    """
    mocker.patch("ahriman.core.database.SQLite.load", return_value=database)
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    _, repository_id = configuration.check_loaded()
    return Application(repository_id, configuration, report=False)


@pytest.fixture
def args() -> argparse.Namespace:
    """
    fixture for command line arguments

    Returns:
        argparse.Namespace: command line arguments test instance
    """
    return argparse.Namespace(architecture=None, lock=None, force=False, unsafe=False, report=False,
                              repository=None, repository_id=None, wait_timeout=-1)


@pytest.fixture
def lock(args: argparse.Namespace, configuration: Configuration) -> Lock:
    """
    fixture for file lock

    Args:
        args(argparse.Namespace): command line arguments fixture
        configuration(Configuration): configuration fixture

    Returns:
        Lock: file lock test instance
    """
    _, repository_id = configuration.check_loaded()
    return Lock(args, repository_id, configuration)


@pytest.fixture
def parser() -> argparse.ArgumentParser:
    """
    fixture for command line arguments parser

    Returns:
        argparse.ArgumentParser: command line arguments parser test instance
    """
    return _parser()
