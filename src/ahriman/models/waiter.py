#
# Copyright (c) 2021-2023 ahriman team.
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

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import ParamSpec


Params = ParamSpec("Params")


@dataclass(frozen=True)
class Waiter:
    """
    simple waiter implementation

    Attributes:
        interval(int): interval in seconds between checks
        start_time(float): monotonic time of the waiter start. More likely must not be assigned explicitly
        wait_timeout(int): timeout in seconds to wait for. Negative value will result in immediate exit. Zero value
    means infinite timeout
    """

    wait_timeout: int
    start_time: float = field(default_factory=time.monotonic, kw_only=True)
    interval: int = field(default=10, kw_only=True)

    def is_timed_out(self) -> bool:
        """
        check if timer is out

        Returns:
            bool: True in case current monotonic time is more than :attr:`start_time` and :attr:`wait_timeout`
            doesn't equal to 0
        """
        since_start: float = time.monotonic() - self.start_time
        return self.wait_timeout != 0 and since_start > self.wait_timeout

    def wait(self, in_progress: Callable[Params, bool], *args: Params.args, **kwargs: Params.kwargs) -> float:
        """
        wait until requirements are not met

        Args:
            in_progress(Callable[Params, bool]): function to check if timer should wait for another cycle
            *args(Params.args): positional arguments for check call
            **kwargs(Params.kwargs): keyword arguments for check call

        Returns:
            float: consumed time in seconds
        """
        while not self.is_timed_out() and in_progress(*args, **kwargs):
            time.sleep(self.interval)

        return time.monotonic() - self.start_time
