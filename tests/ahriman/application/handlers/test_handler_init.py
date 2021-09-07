import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers import Init
from ahriman.core.configuration import Configuration


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    create_tree_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.create_tree")
    init_mock = mocker.patch("ahriman.core.alpm.repo.Repo.init")

    Init.run(args, "x86_64", configuration, True)
    create_tree_mock.assert_called_once()
    init_mock.assert_called_once()
