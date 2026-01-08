#
# Copyright (c) 2021-2026 ahriman team.
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
import time

from types import TracebackType
from typing import Literal, Self

from ahriman.core.exceptions import InitializeError


class MetricsTimer:
    """
    metrics implementation

    Attributes:
        start_time(float | None): timer start time in monotonic time

    Examples:
        This class implements simple timer which allows to measure the time elapsed of the function. Usually it should
        be used like::

            >>> with MetricsTimer() as timer:
            >>>     do_something()
            >>>     print("Time elapsed for first function: %f", timer.elapsed)
            >>>     do_something_different()
            >>>     print("Time elapsed for all functions: %f", timer.elapsed)
    """

    def __init__(self) -> None:
        """"""
        self.start_time: float | None = None

    @property
    def elapsed(self) -> float:
        """
        get elapsed time since the start of the timer

        Returns:
            float: time elapsed in seconds

        Raises:
            InitializeError: in case if timer was not initialized correctly
        """
        if self.start_time is None:
            raise InitializeError("Timer must be started in the context manager")

        stop_time = time.monotonic()
        consumed_time_ms = int(1000 * (stop_time - self.start_time))
        return consumed_time_ms / 1000

    def __enter__(self) -> Self:
        """
        start timer context

        Returns:
            Self: always instance of self
        """
        self.start_time = time.monotonic()
        return self

    def __exit__(self, exc_type: type[Exception] | None, exc_val: Exception | None,
                 exc_tb: TracebackType) -> Literal[False]:
        """
        finish timer context

        Args:
            exc_type(type[Exception] | None): exception type name if any
            exc_val(Exception | None): exception raised if any
            exc_tb(TracebackType): exception traceback if any

        Returns:
            Literal[False]: always ``False`` (do not suppress any exception)
        """
        return False
