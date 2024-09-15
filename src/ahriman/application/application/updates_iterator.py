#
# Copyright (c) 2021-2024 ahriman team.
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

from collections.abc import Iterator
from typing import Self

from ahriman.application.application import Application
from ahriman.core.tree import Tree


class UpdatesIterator(Iterator[list[str] | None]):
    """
    class-helper for iteration over packages to check for updates. It yields list of packages which were not yet
    updated

    Attributes:
        application(Application): application instance
        interval(int): predefined interval for updates. The updates will be split into chunks in the way in which all
            packages will be updated in the specified interval
        updated_packages(set[str]): list of packages which have been already updated

    Examples:
        Typical usage of this class is something like:

            >>> application = ...
            >>> iterator = UpdatesIterator(application, None)
            >>>
            >>> for updates in iterator:
            >>>     print(updates)
    """

    def __init__(self, application: Application, interval: int) -> None:
        """
        Args:
            application(Application): application instance
            interval(int): predefined interval for updates
        """
        self.application = application
        self.interval = interval

        self.updated_packages: set[str] = set()

    def select_packages(self) -> tuple[list[str] | None, int]:
        """
        select next packages partition for updates

        Returns:
            tuple[list[str] | None, int]: packages partition for updates if any and total amount of partitions.
        """
        packages = self.application.repository.packages()
        if not packages:  # empty repository case
            return None, 1

        # split packages to the maximal available amount of chunks
        partitions = Tree.partition(packages, count=len(packages))
        frequency = len(partitions)  # must be always not-empty

        for partition in partitions:
            bases = [package.base for package in partition]
            # check if all packages from this partition have been already updated
            if self.updated_packages.issuperset(bases):
                continue
            # there are packages which were not checked yet, return them
            return bases, frequency

        # in this case there is nothing to update or repository is empty
        self.updated_packages.clear()

        # extract bases from the first partition and return them
        bases = [package.base for package in next(iter(partitions))]
        return bases, frequency

    def __iter__(self) -> Self:
        """
        base iterator method

        Returns:
            Self: iterator instance
        """
        return self

    def __next__(self) -> list[str] | None:
        """
        retrieve next element in the iterator. This method will delay result for the amount of time equals
        :attr:`interval` divided by the amount of chunks

        Returns:
            list[str] | None: next packages chunk to be updated. ``None`` means no updates
        """
        to_update, frequency = self.select_packages()
        if to_update is not None:
            # update cached built packages
            self.updated_packages.update(to_update)

        # wait for update before emit
        time.sleep(self.interval / frequency)

        return to_update


class FixedUpdatesIterator(UpdatesIterator):
    """
    implementation of the :class:`UpdatesIterator` which always emits empty list, which is the same as update all
    """

    def select_packages(self) -> tuple[list[str] | None, int]:
        """
        select next packages partition for updates

        Returns:
            tuple[list[str] | None, int]: packages partition for updates if any and total amount of partitions.
        """
        return [], 1
