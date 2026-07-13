import argparse
import dataclasses
import pytest

from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.application.handlers.search import Search
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import OptionError
from ahriman.core.repository import Repository
from ahriman.models.aur_package import AURPackage


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
        args(argparse.Namespace): command line arguments fixture

    Returns:
        argparse.Namespace: generated arguments for these test cases
    """
    args.search = ["ahriman"]
    args.exit_code = False
    args.info = False
    args.sort_by = "name"
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, repository: Repository,
             aur_package_ahriman: AURPackage, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    aur_search_mock = mocker.patch("ahriman.core.alpm.remote.AUR.multisearch", return_value=[aur_package_ahriman])
    official_search_mock = mocker.patch("ahriman.core.alpm.remote.Official.multisearch",
                                        return_value=[aur_package_ahriman])
    check_mock = mocker.patch("ahriman.application.handlers.handler.Handler.check_status")
    print_mock = mocker.patch("ahriman.core.formatters.Printer.print")

    _, repository_id = configuration.check_loaded()
    Search.run(args, repository_id, configuration, report=False)
    aur_search_mock.assert_called_once_with("ahriman")
    official_search_mock.assert_called_once_with("ahriman")
    check_mock.assert_called_once_with(False, True)
    print_mock.assert_has_calls([
        MockCall(verbose=False, log_fn=pytest.helpers.anyvar(int), separator=": "),
        MockCall(verbose=False, log_fn=pytest.helpers.anyvar(int), separator=": "),
    ])


def test_run_empty_exception(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                             mocker: MockerFixture) -> None:
    """
    must raise ExitCode exception on empty result list
    """
    args = _default_args(args)
    args.exit_code = True
    mocker.patch("ahriman.core.alpm.remote.AUR.multisearch", return_value=[])
    mocker.patch("ahriman.core.alpm.remote.Official.multisearch", return_value=[])
    mocker.patch("ahriman.core.formatters.Printer.print")
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    check_mock = mocker.patch("ahriman.application.handlers.handler.Handler.check_status")

    _, repository_id = configuration.check_loaded()
    Search.run(args, repository_id, configuration, report=False)
    check_mock.assert_called_once_with(True, False)


def test_run_sort(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                  aur_package_ahriman: AURPackage, mocker: MockerFixture) -> None:
    """
    must run command with sorting
    """
    args = _default_args(args)
    mocker.patch("ahriman.core.alpm.remote.AUR.multisearch", return_value=[aur_package_ahriman])
    mocker.patch("ahriman.core.alpm.remote.Official.multisearch", return_value=[])
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    sort_mock = mocker.patch("ahriman.application.handlers.search.Search.sort")

    _, repository_id = configuration.check_loaded()
    Search.run(args, repository_id, configuration, report=False)
    sort_mock.assert_has_calls([
        MockCall([], "name"), MockCall().__iter__(),
        MockCall([aur_package_ahriman], "name"), MockCall().__iter__()
    ])


def test_run_sort_by(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                     aur_package_ahriman: AURPackage, mocker: MockerFixture) -> None:
    """
    must run command with sorting by specified field
    """
    args = _default_args(args)
    args.sort_by = "field"
    mocker.patch("ahriman.core.alpm.remote.AUR.multisearch", return_value=[aur_package_ahriman])
    mocker.patch("ahriman.core.alpm.remote.Official.multisearch", return_value=[])
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    sort_mock = mocker.patch("ahriman.application.handlers.search.Search.sort")

    _, repository_id = configuration.check_loaded()
    Search.run(args, repository_id, configuration, report=False)
    sort_mock.assert_has_calls([
        MockCall([], "field"), MockCall().__iter__(),
        MockCall([aur_package_ahriman], "field"), MockCall().__iter__()
    ])


def test_sort(aur_package_ahriman: AURPackage) -> None:
    """
    must sort package list
    """
    another = dataclasses.replace(aur_package_ahriman, name="1", package_base="base")
    # sort by name
    assert Search.sort([aur_package_ahriman, another], "name") == [another, aur_package_ahriman]
    # sort by another field
    assert Search.sort([aur_package_ahriman, another], "package_base") == [aur_package_ahriman, another]
    # sort by field with the same values
    assert Search.sort([aur_package_ahriman, another], "version") == [another, aur_package_ahriman]


def test_sort_exception(aur_package_ahriman: AURPackage) -> None:
    """
    must raise an exception on unknown sorting field
    """
    with pytest.raises(OptionError):
        Search.sort([aur_package_ahriman], "random_field")


def test_disallow_multi_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not Search.ALLOW_MULTI_ARCHITECTURE_RUN


def test_sort_fields(aur_package_ahriman: AURPackage) -> None:
    """
    must store valid field list which are allowed to be used for sorting
    """
    expected = {field.name for field in dataclasses.fields(AURPackage)}
    assert all(field in expected for field in Search.SORT_FIELDS)
    assert all(not isinstance(getattr(aur_package_ahriman, field), list) for field in Search.SORT_FIELDS)
