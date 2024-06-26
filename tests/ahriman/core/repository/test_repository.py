from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.repository import Repository
from ahriman.core.sign.gpg import GPG
from ahriman.core.status import Client


def test_load(configuration: Configuration, database: SQLite, mocker: MockerFixture) -> None:
    """
    must correctly load instance
    """
    context_mock = mocker.patch("ahriman.core.repository.Repository._set_context")
    _, repository_id = configuration.check_loaded()

    Repository.load(repository_id, configuration, database, report=False)
    context_mock.assert_called_once_with()


def test_set_context(configuration: Configuration, database: SQLite, mocker: MockerFixture) -> None:
    """
    must set context variables
    """
    set_mock = mocker.patch("ahriman.core._Context.set")
    _, repository_id = configuration.check_loaded()

    instance = Repository.load(repository_id, configuration, database, report=False)
    set_mock.assert_has_calls([
        MockCall(SQLite, instance.database),
        MockCall(Configuration, instance.configuration),
        MockCall(Pacman, instance.pacman),
        MockCall(GPG, instance.sign),
        MockCall(Client, instance.reporter),
        MockCall(Repository, instance),
    ])
