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
import contextlib

from typing import Generator

from ahriman.core.status import Client
from ahriman.models.event import Event, EventType
from ahriman.models.metrics_timer import MetricsTimer


class EventLogger:
    """
    wrapper for logging events

    Attributes:
        reporter(Client): build status reporter instance
    """

    reporter: Client

    def event(self, package_base: str, event: EventType, message: str | None = None) -> None:
        """
        log single event. For timed events use context manager :func:`in_event()` instead

        Args:
            package_base(str): package base name
            event(EventType): event type to be logged on success action
            message(str | None, optional): optional message describing the action (Default value = None)

        Examples:
            This method must be used as simple wrapper for :class:`ahriman.core.status.Client` methods, e.g.::

                >>> do_something()
                >>> self.event(package_base, EventType.PackageUpdated)
        """
        self.reporter.event_add(Event(event, package_base, message))

    @contextlib.contextmanager
    def in_event(self, package_base: str, event: EventType, message: str | None = None,
                 failure: EventType | None = None) -> Generator[None, None, None]:
        """
        perform action in package context and log event with time elapsed

        Args:
            package_base(str): package base name
            event(EventType): event type to be logged on success action
            message(str | None, optional): optional message describing the action (Default value = None)
            failure(EventType | None, optional): event type to be logged on exception (Default value = None)

        Examples:
            This method must be used to perform action in context with time measurement::

                >>> with self.in_event(package_base, EventType.PackageUpdated):
                >>>     do_something()

            Additional parameter ``failure`` can be set in order to emit an event on exception occured. If none set
            (default), then no event will be recorded on exception
        """
        with MetricsTimer() as timer:
            try:
                yield
                self.reporter.event_add(Event(event, package_base, message, took=timer.elapsed))
            except Exception:
                if failure is not None:
                    self.reporter.event_add(Event(failure, package_base, took=timer.elapsed))
                raise
