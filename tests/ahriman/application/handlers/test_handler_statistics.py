import argparse
import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.application.handlers import Statistics
from ahriman.core.configuration import Configuration
from ahriman.core.repository import Repository
from ahriman.core.utils import pretty_datetime, utcnow
from ahriman.models.event import Event, EventType
from ahriman.models.package import Package


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
        args(argparse.Namespace): command line arguments fixture

    Returns:
        argparse.Namespace: generated arguments for these test cases
    """
    args.chart = None
    args.event = EventType.PackageUpdated
    args.from_date = None
    args.limit = -1
    args.offset = 0
    args.package = None
    args.to_date = None
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, repository: Repository,
             mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    events = [Event("1", "1"), Event("2", "2")]
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    events_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.event_get", return_value=events)
    application_mock = mocker.patch("ahriman.application.handlers.Statistics.stats_per_package")

    _, repository_id = configuration.check_loaded()
    Statistics.run(args, repository_id, configuration, report=False)
    events_mock.assert_called_once_with(args.event, args.package, None, None, args.limit, args.offset)
    application_mock.assert_called_once_with(args.event, events, args.chart)


def test_run_for_package(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                         package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must run command for specific package
    """
    args = _default_args(args)
    args.package = package_ahriman.base
    events = [Event("1", "1"), Event("2", "2")]
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    events_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.event_get", return_value=events)
    application_mock = mocker.patch("ahriman.application.handlers.Statistics.stats_for_package")

    _, repository_id = configuration.check_loaded()
    Statistics.run(args, repository_id, configuration, report=False)
    events_mock.assert_called_once_with(args.event, args.package, None, None, args.limit, args.offset)
    application_mock.assert_called_once_with(args.event, events, args.chart)


def test_run_convert_from_date(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                               mocker: MockerFixture) -> None:
    """
    must convert from date
    """
    args = _default_args(args)
    date = utcnow()
    args.from_date = date.isoformat()
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    mocker.patch("ahriman.application.handlers.Statistics.stats_per_package")
    events_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.event_get", return_value=[])

    _, repository_id = configuration.check_loaded()
    Statistics.run(args, repository_id, configuration, report=False)
    events_mock.assert_called_once_with(args.event, args.package, date.timestamp(), None, args.limit, args.offset)


def test_run_convert_to_date(args: argparse.Namespace, configuration: Configuration, repository: Repository,
                             mocker: MockerFixture) -> None:
    """
    must convert to date
    """
    args = _default_args(args)
    date = utcnow()
    args.to_date = date.isoformat()
    mocker.patch("ahriman.core.repository.Repository.load", return_value=repository)
    mocker.patch("ahriman.application.handlers.Statistics.stats_per_package")
    events_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.event_get", return_value=[])

    _, repository_id = configuration.check_loaded()
    Statistics.run(args, repository_id, configuration, report=False)
    events_mock.assert_called_once_with(args.event, args.package, None, date.timestamp(), args.limit, args.offset)


def test_event_stats(mocker: MockerFixture) -> None:
    """
    must print event stats
    """
    print_mock = mocker.patch("ahriman.core.formatters.Printer.print")
    events = [Event("event", "1"), Event("event", "2", took=42.0)]

    Statistics.event_stats("event", events)
    print_mock.assert_called_once_with(verbose=True, log_fn=pytest.helpers.anyvar(int), separator=": ")


def test_plot_packages(mocker: MockerFixture) -> None:
    """
    must plot chart for packages
    """
    plot_mock = mocker.patch("matplotlib.pyplot.bar")
    save_mock = mocker.patch("matplotlib.pyplot.savefig")
    local = Path("local")

    Statistics.plot_packages("event", {"1": 1, "2": 2}, local)
    plot_mock.assert_called_once_with(["1", "2"], [1, 2])
    save_mock.assert_called_once_with(local)


def test_plot_times(mocker: MockerFixture) -> None:
    """
    must plot chart for durations
    """
    plot_mock = mocker.patch("matplotlib.pyplot.plot")
    save_mock = mocker.patch("matplotlib.pyplot.savefig")
    local = Path("local")

    Statistics.plot_times("event", [
        Event("", "", created=1, took=2),
        Event("", "", created=3, took=4),
    ], local)
    plot_mock.assert_called_once_with((pretty_datetime(1), pretty_datetime(3)), (2, 4))
    save_mock.assert_called_once_with(local)


def test_stats_for_package(mocker: MockerFixture) -> None:
    """
    must print statistics for the package
    """
    events = [Event("event", "1"), Event("event", "1")]
    events_mock = mocker.patch("ahriman.application.handlers.Statistics.event_stats")
    chart_plot = mocker.patch("ahriman.application.handlers.Statistics.plot_times")

    Statistics.stats_for_package("event", events, None)
    events_mock.assert_called_once_with("event", events)
    chart_plot.assert_not_called()


def test_stats_for_package_with_chart(mocker: MockerFixture) -> None:
    """
    must generate chart for package stats
    """
    local = Path("local")
    events = [Event("event", "1"), Event("event", "1")]
    mocker.patch("ahriman.application.handlers.Statistics.event_stats")
    chart_plot = mocker.patch("ahriman.application.handlers.Statistics.plot_times")

    Statistics.stats_for_package("event", events, local)
    chart_plot.assert_called_once_with("event", events, local)


def test_stats_per_package(mocker: MockerFixture) -> None:
    """
    must print statistics per package
    """
    events = [Event("event", "1"), Event("event", "2"), Event("event", "1")]
    print_mock = mocker.patch("ahriman.core.formatters.Printer.print")
    events_mock = mocker.patch("ahriman.application.handlers.Statistics.event_stats")
    chart_plot = mocker.patch("ahriman.application.handlers.Statistics.plot_packages")

    Statistics.stats_per_package("event", events, None)
    print_mock.assert_has_calls([
        MockCall(verbose=True, log_fn=pytest.helpers.anyvar(int), separator=": "),
        MockCall(verbose=True, log_fn=pytest.helpers.anyvar(int), separator=": "),
    ])
    events_mock.assert_called_once_with("event", events)
    chart_plot.assert_not_called()


def test_stats_per_package_with_chart(mocker: MockerFixture) -> None:
    """
    must print statistics per package with chart
    """
    local = Path("local")
    events = [Event("event", "1"), Event("event", "2"), Event("event", "1")]
    mocker.patch("ahriman.application.handlers.Statistics.event_stats")
    chart_plot = mocker.patch("ahriman.application.handlers.Statistics.plot_packages")

    Statistics.stats_per_package("event", events, local)
    chart_plot.assert_called_once_with("event", {"1": 2, "2": 1}, local)
