from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.repository.properties import Properties


def test_create_tree_on_load(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must create tree on load
    """
    create_tree_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.create_tree")
    Properties("x86_64", configuration)

    create_tree_mock.assert_called_once()
