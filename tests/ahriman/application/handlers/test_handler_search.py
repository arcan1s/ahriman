import argparse
import dataclasses
import pytest

from pytest_mock import MockerFixture

from ahriman.application.handlers import Search
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import InvalidOption
from ahriman.models.aur_package import AURPackage


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases
    :param args: command line arguments fixture
    :return: generated arguments for these test cases
    """
    args.search = ["ahriman"]
    args.info = False
    args.sort_by = "name"
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, aur_package_ahriman: AURPackage,
             mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    search_mock = mocker.patch("ahriman.core.alpm.aur.AUR.multisearch", return_value=[aur_package_ahriman])
    print_mock = mocker.patch("ahriman.application.formatters.printer.Printer.print")

    Search.run(args, "x86_64", configuration, True, False)
    search_mock.assert_called_once_with("ahriman")
    print_mock.assert_called_once_with(False)


def test_run_sort(args: argparse.Namespace, configuration: Configuration, aur_package_ahriman: AURPackage,
                  mocker: MockerFixture) -> None:
    """
    must run command with sorting
    """
    args = _default_args(args)
    mocker.patch("ahriman.core.alpm.aur.AUR.multisearch", return_value=[aur_package_ahriman])
    sort_mock = mocker.patch("ahriman.application.handlers.search.Search.sort")

    Search.run(args, "x86_64", configuration, True, False)
    sort_mock.assert_called_once_with([aur_package_ahriman], "name")


def test_run_sort_by(args: argparse.Namespace, configuration: Configuration, aur_package_ahriman: AURPackage,
                     mocker: MockerFixture) -> None:
    """
    must run command with sorting by specified field
    """
    args = _default_args(args)
    args.sort_by = "field"
    mocker.patch("ahriman.core.alpm.aur.AUR.multisearch", return_value=[aur_package_ahriman])
    sort_mock = mocker.patch("ahriman.application.handlers.search.Search.sort")

    Search.run(args, "x86_64", configuration, True, False)
    sort_mock.assert_called_once_with([aur_package_ahriman], "field")


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
    with pytest.raises(InvalidOption):
        Search.sort([aur_package_ahriman], "random_field")


def test_disallow_auto_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not Search.ALLOW_AUTO_ARCHITECTURE_RUN


def test_sort_fields() -> None:
    """
    must store valid field list which are allowed to be used for sorting
    """
    expected = {pair.name for pair in dataclasses.fields(AURPackage)}
    assert all(field in expected for field in Search.SORT_FIELDS)
