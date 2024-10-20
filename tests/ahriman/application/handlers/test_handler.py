import argparse
import pytest

from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.application.handlers import Handler
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import ExitCode, MissingArchitectureError, MultipleArchitecturesError
from ahriman.models.log_handler import LogHandler
from ahriman.models.repository_id import RepositoryId


def test_call(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must call inside lock
    """
    args.configuration = Path("")
    args.log_handler = LogHandler.Console
    args.quiet = False
    args.report = False
    mocker.patch("ahriman.application.handlers.Handler.run")
    configuration_mock = mocker.patch("ahriman.core.configuration.Configuration.from_path", return_value=configuration)
    log_handler_mock = mocker.patch("ahriman.core.log.log_loader.LogLoader.handler", return_value=args.log_handler)
    log_load_mock = mocker.patch("ahriman.core.log.log_loader.LogLoader.load")
    enter_mock = mocker.patch("ahriman.application.lock.Lock.__enter__")
    exit_mock = mocker.patch("ahriman.application.lock.Lock.__exit__")

    _, repository_id = configuration.check_loaded()
    assert Handler.call(args, repository_id)
    configuration_mock.assert_called_once_with(args.configuration, repository_id)
    log_handler_mock.assert_called_once_with(args.log_handler)
    log_load_mock.assert_called_once_with(
        repository_id,
        configuration,
        args.log_handler,
        quiet=args.quiet,
        report=args.report)
    enter_mock.assert_called_once_with()
    exit_mock.assert_called_once_with(None, None, None)


def test_call_exception(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must process exception
    """
    args.configuration = Path("")
    args.quiet = False
    mocker.patch("ahriman.core.configuration.Configuration.from_path", side_effect=Exception())
    logging_mock = mocker.patch("logging.Logger.exception")

    _, repository_id = configuration.check_loaded()
    assert not Handler.call(args, repository_id)
    logging_mock.assert_called_once_with(pytest.helpers.anyvar(str, strict=True))


def test_call_exit_code(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must process exitcode exception
    """
    args.configuration = Path("")
    args.quiet = False
    mocker.patch("ahriman.core.configuration.Configuration.from_path", side_effect=ExitCode())
    logging_mock = mocker.patch("logging.Logger.exception")

    _, repository_id = configuration.check_loaded()
    assert not Handler.call(args, repository_id)
    logging_mock.assert_not_called()


def test_execute(args: argparse.Namespace, mocker: MockerFixture) -> None:
    """
    must run execution in multiple processes
    """
    ids = [
        RepositoryId("i686", "aur"),
        RepositoryId("x86_64", "aur"),
    ]
    mocker.patch("ahriman.application.handlers.Handler.repositories_extract", return_value=ids)
    starmap_mock = mocker.patch("multiprocessing.pool.Pool.starmap")

    Handler.execute(args)
    starmap_mock.assert_called_once_with(Handler.call, [(args, repository_id) for repository_id in ids])


def test_execute_multiple_not_supported(args: argparse.Namespace, mocker: MockerFixture) -> None:
    """
    must raise an exception if multiple architectures are not supported by the handler
    """
    args.command = "web"
    mocker.patch("ahriman.application.handlers.Handler.repositories_extract", return_value=[
        RepositoryId("i686", "aur"),
        RepositoryId("x86_64", "aur"),
    ])
    mocker.patch.object(Handler, "ALLOW_MULTI_ARCHITECTURE_RUN", False)

    with pytest.raises(MultipleArchitecturesError):
        Handler.execute(args)


def test_execute_single(args: argparse.Namespace, mocker: MockerFixture) -> None:
    """
    must run execution in current process if only one architecture supplied
    """
    mocker.patch("ahriman.application.handlers.Handler.repositories_extract", return_value=[
        RepositoryId("x86_64", "aur"),
    ])
    starmap_mock = mocker.patch("multiprocessing.pool.Pool.starmap")

    Handler.execute(args)
    starmap_mock.assert_not_called()


def test_run(args: argparse.Namespace, configuration: Configuration) -> None:
    """
    must raise NotImplemented for missing method
    """
    _, repository_id = configuration.check_loaded()
    with pytest.raises(NotImplementedError):
        Handler.run(args, repository_id, configuration, report=True)


def test_check_status() -> None:
    """
    must raise exception in case if predicate is True and enabled
    """
    Handler.check_status(False, True)
    Handler.check_status(False, False)
    Handler.check_status(False, lambda: True)
    Handler.check_status(False, lambda: False)

    Handler.check_status(True, True)
    with pytest.raises(ExitCode):
        Handler.check_status(True, False)
    Handler.check_status(True, lambda: True)
    with pytest.raises(ExitCode):
        Handler.check_status(True, lambda: False)


def test_repositories_extract(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must generate list of available repositories based on flags
    """
    args.architecture = "arch"
    args.configuration = configuration.path
    args.repository = "repo"
    known_architectures_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.known_architectures")
    known_repositories_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.known_repositories")

    assert Handler.repositories_extract(args) == [RepositoryId("arch", "repo")]
    known_architectures_mock.assert_not_called()
    known_repositories_mock.assert_not_called()


def test_repositories_extract_repository(args: argparse.Namespace, configuration: Configuration,
                                         mocker: MockerFixture) -> None:
    """
    must generate list of available repositories based on flags and tree
    """
    args.architecture = "arch"
    args.configuration = configuration.path
    known_architectures_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.known_architectures")
    known_repositories_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.known_repositories",
                                           return_value={"repo"})

    assert Handler.repositories_extract(args) == [RepositoryId("arch", "repo")]
    known_architectures_mock.assert_not_called()
    known_repositories_mock.assert_called_once_with(configuration.repository_paths.root)


def test_repositories_extract_repository_legacy(args: argparse.Namespace, configuration: Configuration,
                                                mocker: MockerFixture) -> None:
    """
    must generate list of available repositories based on flags and tree (legacy mode)
    """
    args.architecture = "arch"
    args.configuration = configuration.path
    known_architectures_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.known_architectures")
    known_repositories_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.known_repositories",
                                           return_value=set())

    assert Handler.repositories_extract(args) == [RepositoryId("arch", "aur")]
    known_architectures_mock.assert_not_called()
    known_repositories_mock.assert_called_once_with(configuration.repository_paths.root)


def test_repositories_extract_architecture(args: argparse.Namespace, configuration: Configuration,
                                           mocker: MockerFixture) -> None:
    """
    must read repository name from config
    """
    args.configuration = configuration.path
    args.repository = "repo"
    known_architectures_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.known_architectures",
                                            return_value={"arch"})
    known_repositories_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.known_repositories")

    assert Handler.repositories_extract(args) == [RepositoryId("arch", "repo")]
    known_architectures_mock.assert_called_once_with(configuration.repository_paths.root, "repo")
    known_repositories_mock.assert_not_called()


def test_repositories_extract_empty(args: argparse.Namespace, configuration: Configuration,
                                    mocker: MockerFixture) -> None:
    """
    must raise exception if no available architectures found
    """
    args.command = "config"
    args.configuration = configuration.path
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.known_architectures", return_value=set())
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.known_repositories", return_value=set())

    with pytest.raises(MissingArchitectureError):
        Handler.repositories_extract(args)


def test_repositories_extract_systemd(args: argparse.Namespace, configuration: Configuration,
                                      mocker: MockerFixture) -> None:
    """
    must extract repository list for systemd units
    """
    args.configuration = configuration.path
    args.repository_id = "i686/some/repo/name"
    known_architectures_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.known_architectures")
    known_repositories_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.known_repositories")

    assert Handler.repositories_extract(args) == [RepositoryId("i686", "some-repo-name")]
    known_architectures_mock.assert_not_called()
    known_repositories_mock.assert_not_called()


def test_repositories_extract_systemd_with_dash(args: argparse.Namespace, configuration: Configuration,
                                                mocker: MockerFixture) -> None:
    """
    must extract repository list by using dash separated identifier
    """
    args.configuration = configuration.path
    args.repository_id = "i686-some-repo-name"
    known_architectures_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.known_architectures")
    known_repositories_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.known_repositories")

    assert Handler.repositories_extract(args) == [RepositoryId("i686", "some-repo-name")]
    known_architectures_mock.assert_not_called()
    known_repositories_mock.assert_not_called()


def test_repositories_extract_systemd_legacy(args: argparse.Namespace, configuration: Configuration,
                                             mocker: MockerFixture) -> None:
    """
    must extract repository list for systemd units in legacy format
    """
    args.configuration = configuration.path
    args.repository_id = "i686"
    known_architectures_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.known_architectures")
    known_repositories_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.known_repositories",
                                           return_value=set())

    assert Handler.repositories_extract(args) == [RepositoryId("i686", "aur")]
    known_architectures_mock.assert_not_called()
    known_repositories_mock.assert_called_once_with(configuration.repository_paths.root)
