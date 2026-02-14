from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.repository import Explorer
from ahriman.models.repository_id import RepositoryId


def test_repositories_extract(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must generate list of available repositories based on arguments
    """
    known_architectures_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.known_architectures")
    known_repositories_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.known_repositories")

    assert Explorer.repositories_extract(configuration, "repo", "arch") == [RepositoryId("arch", "repo")]
    known_architectures_mock.assert_not_called()
    known_repositories_mock.assert_not_called()


def test_repositories_extract_repository(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must generate list of available repositories based on arguments and tree
    """
    known_architectures_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.known_architectures")
    known_repositories_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.known_repositories",
                                           return_value={"repo"})

    assert Explorer.repositories_extract(configuration, architecture="arch") == [RepositoryId("arch", "repo")]
    known_architectures_mock.assert_not_called()
    known_repositories_mock.assert_called_once_with(configuration.repository_paths.root)


def test_repositories_extract_repository_legacy(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must generate list of available repositories based on arguments and tree (legacy mode)
    """
    known_architectures_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.known_architectures")
    known_repositories_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.known_repositories",
                                           return_value=set())

    assert Explorer.repositories_extract(configuration, architecture="arch") == [RepositoryId("arch", "aur")]
    known_architectures_mock.assert_not_called()
    known_repositories_mock.assert_called_once_with(configuration.repository_paths.root)


def test_repositories_extract_architecture(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must read repository name from config
    """
    known_architectures_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.known_architectures",
                                            return_value={"arch"})
    known_repositories_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.known_repositories")

    assert Explorer.repositories_extract(configuration, repository="repo") == [RepositoryId("arch", "repo")]
    known_architectures_mock.assert_called_once_with(configuration.repository_paths.root, "repo")
    known_repositories_mock.assert_not_called()
