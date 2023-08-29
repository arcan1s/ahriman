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
    log_handler_mock = mocker.patch("ahriman.core.log.Log.handler", return_value=args.log_handler)
    log_load_mock = mocker.patch("ahriman.core.log.Log.load")
    enter_mock = mocker.patch("ahriman.application.lock.Lock.__enter__")
    exit_mock = mocker.patch("ahriman.application.lock.Lock.__exit__")

    _, repository_id = configuration.check_loaded()
    assert Handler.call(args, repository_id)
    configuration_mock.assert_called_once_with(args.configuration, repository_id)
    log_handler_mock.assert_called_once_with(args.log_handler)
    log_load_mock.assert_called_once_with(configuration, args.log_handler, quiet=args.quiet, report=args.report)
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
        RepositoryId("i686", "aur-clone"),
        RepositoryId("x86_64", "aur-clone"),
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
        RepositoryId("i686", "aur-clone"),
        RepositoryId("x86_64", "aur-clone"),
    ])
    mocker.patch.object(Handler, "ALLOW_MULTI_ARCHITECTURE_RUN", False)

    with pytest.raises(MultipleArchitecturesError):
        Handler.execute(args)


def test_execute_single(args: argparse.Namespace, mocker: MockerFixture) -> None:
    """
    must run execution in current process if only one architecture supplied
    """
    mocker.patch("ahriman.application.handlers.Handler.repositories_extract", return_value=[
        RepositoryId("x86_64", "aur-clone"),
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


def test_repositories_extract(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must generate list of available architectures
    """
    args.configuration = configuration.path
    _, repository_id = configuration.check_loaded()
    known_architectures_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.known_architectures")

    Handler.repositories_extract(args)
    known_architectures_mock.assert_called_once_with(configuration.getpath("repository", "root"), repository_id.name)


def test_repositories_extract_empty(args: argparse.Namespace, configuration: Configuration,
                                    mocker: MockerFixture) -> None:
    """
    must raise exception if no available architectures found
    """
    args.command = "config"
    args.configuration = configuration.path
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.known_architectures", return_value=set())

    with pytest.raises(MissingArchitectureError):
        Handler.repositories_extract(args)


def test_repositories_extract_exception(args: argparse.Namespace, mocker: MockerFixture) -> None:
    """
    must raise exception on missing architectures
    """
    args.command = "config"
    mocker.patch.object(Handler, "ALLOW_AUTO_ARCHITECTURE_RUN", False)
    with pytest.raises(MissingArchitectureError):
        Handler.repositories_extract(args)


def test_repositories_extract_specified(args: argparse.Namespace, configuration: Configuration) -> None:
    """
    must return architecture list if it has been specified
    """
    args.configuration = configuration.path
    args.architecture = ["i686", "x86_64"]
    args.repository = []
    _, repository_id = configuration.check_loaded()

    ids = [RepositoryId(architecture, repository_id.name) for architecture in args.architecture]
    assert Handler.repositories_extract(args) == sorted(set(ids))


def test_repositories_extract_specified_with_repository(args: argparse.Namespace, configuration: Configuration) -> None:
    """
    must return architecture list if it has been specified together with repositories
    """
    args.configuration = configuration.path
    args.architecture = ["i686", "x86_64"]
    args.repository = ["repo1", "repo2"]

    ids = [
        RepositoryId(architecture, name)
        for architecture in args.architecture
        for name in args.repository
    ]
    assert Handler.repositories_extract(args) == sorted(set(ids))


def test_check_if_empty() -> None:
    """
    must raise exception in case if predicate is True and enabled
    """
    Handler.check_if_empty(False, False)
    Handler.check_if_empty(True, False)
    Handler.check_if_empty(False, True)
    with pytest.raises(ExitCode):
        Handler.check_if_empty(True, True)
