#
# Copyright (c) 2021-2025 ahriman team.
#
# This file is part of ahriman
# (see https://github.com/arcan1s/ahriman).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import argparse
import datetime
import itertools

from collections.abc import Callable
from pathlib import Path

from ahriman.application.application import Application
from ahriman.application.handlers.handler import Handler, SubParserAction
from ahriman.core.configuration import Configuration
from ahriman.core.formatters import EventStatsPrinter, PackageStatsPrinter
from ahriman.core.utils import enum_values, pretty_datetime
from ahriman.models.event import Event, EventType
from ahriman.models.repository_id import RepositoryId


class Statistics(Handler):
    """
    repository statistics handler
    """

    ALLOW_MULTI_ARCHITECTURE_RUN = False  # conflicting io

    @classmethod
    def run(cls, args: argparse.Namespace, repository_id: RepositoryId, configuration: Configuration, *,
            report: bool) -> None:
        """
        callback for command line

        Args:
            args(argparse.Namespace): command line args
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
            report(bool): force enable or disable reporting
        """
        application = Application(repository_id, configuration, report=True)

        from_date = to_date = None
        if (value := args.from_date) is not None:
            from_date = datetime.datetime.fromisoformat(value).timestamp()
        if (value := args.to_date) is not None:
            to_date = datetime.datetime.fromisoformat(value).timestamp()

        events = application.reporter.event_get(args.event, args.package, from_date, to_date, args.limit, args.offset)

        match args.package:
            case None:
                Statistics.stats_per_package(args.event, events, args.chart)
            case _:
                Statistics.stats_for_package(args.event, events, args.chart)

    @staticmethod
    def _set_repo_statistics_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for repository statistics subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("repo-statistics", help="repository statistics",
                                 description="fetch repository statistics")
        parser.add_argument("package", help="fetch only events for the specified package", nargs="?")
        parser.add_argument("--chart", help="create updates chart and save it to the specified path", type=Path)
        parser.add_argument("-e", "--event", help="event type filter",
                            type=EventType, choices=enum_values(EventType), default=EventType.PackageUpdated)
        parser.add_argument("--from-date", help="only fetch events which are newer than the date")
        parser.add_argument("--limit", help="limit response by specified amount of events", type=int, default=-1)
        parser.add_argument("--offset", help="skip specified amount of events", type=int, default=0)
        parser.add_argument("--to-date", help="only fetch events which are older than the date")
        parser.set_defaults(lock=None, quiet=True, report=False, unsafe=True)
        return parser

    @staticmethod
    def event_stats(event_type: str, events: list[Event]) -> None:
        """
        calculate event stats

        Args:
            event_type(str): event type
            events(list[Event]): list of events
        """
        times = [event.get("took") for event in events if event.get("took") is not None]
        EventStatsPrinter(f"{event_type} duration, s", times)(verbose=True)

    @staticmethod
    def plot_packages(event_type: str, events: dict[str, int], path: Path) -> None:
        """
        plot packages frequency

        Args:
            event_type(str): event type
            events(dict[str, int]): list of events
            path(Path): path to save plot
        """
        from matplotlib import pyplot as plt

        x, y = list(events.keys()), list(events.values())
        plt.bar(x, y)

        plt.xlabel("Package base")
        plt.ylabel("Frequency")
        plt.title(f"Frequency of the {event_type} event per package")

        plt.savefig(path)

    @staticmethod
    def plot_times(event_type: str, events: list[Event], path: Path) -> None:
        """
        plot events timeline

        Args:
            event_type(str): event type
            events(list[Event]): list of events
            path(Path): path to save plot
        """
        from matplotlib import pyplot as plt

        figure = plt.figure()

        x, y = zip(*[(pretty_datetime(event.created), event.get("took")) for event in events])
        plt.plot(x, y)

        plt.xlabel("Event timestamp")
        plt.ylabel("Duration, s")
        plt.title(f"Duration of the {event_type} event")
        figure.autofmt_xdate()

        plt.savefig(path)

    @staticmethod
    def stats_for_package(event_type: str, events: list[Event], chart_path: Path | None) -> None:
        """
        calculate statistics for a package

        Args:
            event_type(str): event type
            events(list[Event]): list of events
            chart_path(Path): path to save plot if any
        """
        # event statistics
        Statistics.event_stats(event_type, events)

        # chart if enabled
        if chart_path is not None:
            Statistics.plot_times(event_type, events, chart_path)

    @staticmethod
    def stats_per_package(event_type: str, events: list[Event], chart_path: Path | None) -> None:
        """
        calculate overall statistics

        Args:
            event_type(str): event type
            events(list[Event]): list of events
            chart_path(Path): path to save plot if any
        """
        key: Callable[[Event], str] = lambda event: event.object_id
        by_object_id = {
            object_id: len(list(related))
            for object_id, related in itertools.groupby(sorted(events, key=key), key=key)
        }

        # distribution per package
        PackageStatsPrinter(by_object_id)(verbose=True)
        EventStatsPrinter(f"{event_type} frequency", list(by_object_id.values()))(verbose=True)

        # event statistics
        Statistics.event_stats(event_type, events)

        # chart if enabled
        if chart_path is not None:
            Statistics.plot_packages(event_type, by_object_id, chart_path)

    arguments = [_set_repo_statistics_parser]
