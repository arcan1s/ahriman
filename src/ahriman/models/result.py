#
# Copyright (c) 2021-2022 ahriman team.
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
from __future__ import annotations

from typing import Any, List, Optional, Iterable

from ahriman.core.exceptions import SuccessFailed
from ahriman.models.package import Package


class Result:
    """
    build result class holder
    """

    def __init__(self, success: Optional[Iterable[Package]] = None, failed: Optional[Iterable[Package]] = None) -> None:
        """
        default constructor

        Args:
          success(Optional[Iterable[Package]], optional): initial list of successes packages (Default value = None)
          failed(Optional[Iterable[Package]], optional): initial list of failed packages (Default value = None)
        """
        success = success or []
        self._success = {package.base: package for package in success}
        failed = failed or []
        self._failed = {package.base: package for package in failed}

    @property
    def failed(self) -> List[Package]:
        """
        Returns:
          List[Package]: list of packages which were failed
        """
        return list(self._failed.values())

    @property
    def is_empty(self) -> bool:
        """
        Returns:
          bool: True in case if success list is empty and False otherwise
        """
        return not bool(self._success)

    @property
    def success(self) -> List[Package]:
        """
        Returns:
          List[Package]: list of packages with success result
        """
        return list(self._success.values())

    def add_failed(self, package: Package) -> None:
        """
        add new package to failed built

        Args:
          package(Package): package with errors during build
        """
        self._failed[package.base] = package

    def add_success(self, package: Package) -> None:
        """
        add new package to success built

        Args:
          package(Package): package built
        """
        self._success[package.base] = package

    # pylint: disable=protected-access
    def merge(self, other: Result) -> Result:
        """
        merge other result into this one. This method assumes that other has fresh info about status and override it

        Args:
          other(Result): instance of the newest result

        Returns:
          Result: updated instance
        """
        for base, package in other._failed.items():
            if base in self._success:
                del self._success[base]
            self.add_failed(package)
        for base, package in other._success.items():
            if base in self._failed:
                raise SuccessFailed(base)
            self.add_success(package)
        return self

    # required for tests at least
    def __eq__(self, other: Any) -> bool:
        """
        check if other is the same object

        Args:
          other(Any): other object instance

        Returns:
          bool: True if the other object is the same and False otherwise
        """
        if not isinstance(other, Result):
            return False
        return self.success == other.success and self.failed == other.failed
