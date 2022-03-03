import argparse

from pytest_mock import MockerFixture

from ahriman.application.handlers import Init
from ahriman.core.configuration import Configuration


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    mocker.patch("ahriman.core.repository.properties.check_user")
    tree_create_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    init_mock = mocker.patch("ahriman.core.alpm.repo.Repo.init")

    Init.run(args, "x86_64", configuration, True)
    tree_create_mock.assert_called_once_with()
    init_mock.assert_called_once_with()


def test_disallow_auto_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not Init.ALLOW_AUTO_ARCHITECTURE_RUN
