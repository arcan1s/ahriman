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
import statistics

from dataclasses import dataclass


@dataclass(frozen=True)
class SeriesStatistics:
    """
    series statistics helper

    Attributes:
        series(list[float | int]): list of values to be processed
    """

    series: list[float | int]

    @property
    def max(self) -> float | int | None:
        """
        get max value in series

        Returns:
            float | int | None: ``None`` if series is empty and maximal value otherwise``
        """
        if self:
            return max(self.series)
        return None

    @property
    def mean(self) -> float | int | None:
        """
        get mean value in series

        Returns:
            float | int | None: ``None`` if series is empty and mean value otherwise
        """
        if self:
            return statistics.mean(self.series)
        return None

    @property
    def min(self) -> float | int | None:
        """
        get min value in series

        Returns:
            float | int | None: ``None`` if series is empty and minimal value otherwise
        """
        if self:
            return min(self.series)
        return None

    @property
    def st_dev(self) -> float | None:
        """
        get standard deviation in series

        Returns:
            float | None: ``None`` if series size is less than 1, 0 if series contains single element and standard
            deviation otherwise
        """
        if not self:
            return None
        if len(self.series) > 1:
            return statistics.stdev(self.series)
        return 0.0

    @property
    def total(self) -> int:
        """
        retrieve amount of elements

        Returns:
            int: the series collection size
        """
        return len(self.series)

    def __bool__(self) -> bool:
        """
        check if series is empty or not

        Returns:
            bool: ``True`` if series contains elements and ``False`` otherwise
        """
        return bool(self.total)
