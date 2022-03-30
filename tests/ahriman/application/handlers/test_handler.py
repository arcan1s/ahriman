import argparse
import pytest

from pathlib import Path
from pytest_mock import MockerFixture

from ahriman.application.handlers import Handler
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import ExitCode, MissingArchitecture, MultipleArchitectures


def test_architectures_extract(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must generate list of available architectures
    """
    args.configuration = configuration.path
    known_architectures_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.known_architectures")

    Handler.architectures_extract(args)
    known_architectures_mock.assert_called_once_with(configuration.getpath("repository", "root"))


def test_architectures_extract_empty(args: argparse.Namespace, configuration: Configuration,
                                     mocker: MockerFixture) -> None:
    """
    must raise exception if no available architectures found
    """
    args.command = "config"
    args.configuration = configuration.path
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.known_architectures", return_value=set())

    with pytest.raises(MissingArchitecture):
        Handler.architectures_extract(args)


def test_architectures_extract_exception(args: argparse.Namespace, mocker: MockerFixture) -> None:
    """
    must raise exception on missing architectures
    """
    args.command = "config"
    mocker.patch.object(Handler, "ALLOW_AUTO_ARCHITECTURE_RUN", False)
    with pytest.raises(MissingArchitecture):
        Handler.architectures_extract(args)


def test_architectures_extract_specified(args: argparse.Namespace) -> None:
    """
    must return architecture list if it has been specified
    """
    architectures = args.architecture = ["i686", "x86_64"]
    assert Handler.architectures_extract(args) == sorted(set(architectures))


def test_call(args: argparse.Namespace, mocker: MockerFixture) -> None:
    """
    must call inside lock
    """
    args.configuration = Path("")
    args.quiet = False
    mocker.patch("ahriman.application.handlers.Handler.run")
    mocker.patch("ahriman.core.configuration.Configuration.from_path")
    enter_mock = mocker.patch("ahriman.application.lock.Lock.__enter__")
    exit_mock = mocker.patch("ahriman.application.lock.Lock.__exit__")

    assert Handler.call(args, "x86_64")
    enter_mock.assert_called_once_with()
    exit_mock.assert_called_once_with(None, None, None)


def test_call_exception(args: argparse.Namespace, mocker: MockerFixture) -> None:
    """
    must process exception
    """
    args.configuration = Path("")
    args.quiet = False
    mocker.patch("ahriman.core.configuration.Configuration.from_path", side_effect=Exception())
    logging_mock = mocker.patch("logging.Logger.exception")

    assert not Handler.call(args, "x86_64")
    logging_mock.assert_called_once_with(pytest.helpers.anyvar(str, strict=True))


def test_call_exit_code(args: argparse.Namespace, mocker: MockerFixture) -> None:
    """
    must process exitcode exception
    """
    args.configuration = Path("")
    args.quiet = False
    mocker.patch("ahriman.core.configuration.Configuration.from_path", side_effect=ExitCode())
    logging_mock = mocker.patch("logging.Logger.exception")

    assert not Handler.call(args, "x86_64")
    logging_mock.assert_not_called()


def test_execute(args: argparse.Namespace, mocker: MockerFixture) -> None:
    """
    must run execution in multiple processes
    """
    args.architecture = ["i686", "x86_64"]
    starmap_mock = mocker.patch("multiprocessing.pool.Pool.starmap")

    Handler.execute(args)
    starmap_mock.assert_called_once_with(Handler.call, [(args, architecture) for architecture in args.architecture])


def test_execute_multiple_not_supported(args: argparse.Namespace, mocker: MockerFixture) -> None:
    """
    must raise an exception if multiple architectures are not supported by the handler
    """
    args.architecture = ["i686", "x86_64"]
    args.command = "web"
    mocker.patch.object(Handler, "ALLOW_MULTI_ARCHITECTURE_RUN", False)

    with pytest.raises(MultipleArchitectures):
        Handler.execute(args)


def test_execute_single(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run execution in current process if only one architecture supplied
    """
    args.architecture = ["x86_64"]
    args.configuration = Path("")
    args.quiet = False
    mocker.patch("ahriman.core.configuration.Configuration.from_path", return_value=configuration)
    starmap_mock = mocker.patch("multiprocessing.pool.Pool.starmap")

    Handler.execute(args)
    starmap_mock.assert_not_called()


def test_run(args: argparse.Namespace, configuration: Configuration) -> None:
    """
    must raise NotImplemented for missing method
    """
    with pytest.raises(NotImplementedError):
        Handler.run(args, "x86_64", configuration, True, True)
