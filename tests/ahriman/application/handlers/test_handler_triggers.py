import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers import Triggers
from ahriman.core.configuration import Configuration
from ahriman.models.result import Result


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    application_mock = mocker.patch("ahriman.core.repository.Repository.process_triggers")

    Triggers.run(args, "x86_64", configuration, True, False)
    application_mock.assert_called_once_with(Result())
