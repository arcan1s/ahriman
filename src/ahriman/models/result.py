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
from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any, ClassVar, Self

from ahriman.models.package import Package


class Result:
    """
    build result class holder

    Attributes:
        STATUS_PRIORITIES(list[str]): (class attribute) list of statues according to their priorities
    """

    STATUS_PRIORITIES: ClassVar[list[str]] = [
        "failed",
        "removed",
        "updated",
        "added",
    ]

    def __init__(self, *, added: Iterable[Package] | None = None, updated: Iterable[Package] | None = None,
                 removed: Iterable[Package] | None = None, failed: Iterable[Package] | None = None) -> None:
        """
        Args:
            added(Iterable[Package] | None, optional): initial list of successfully added packages
                (Default value = None)
            updated(Iterable[Package] | None, optional): initial list of successfully updated packages
                (Default value = None)
            removed(Iterable[Package] | None, optional): initial list of successfully removed packages
                (Default value = None)
            failed(Iterable[Package] | None, optional): initial list of failed packages (Default value = None)
        """
        added = added or []
        self._added = {package.base: package for package in added}

        updated = updated or []
        self._updated = {package.base: package for package in updated}

        removed = removed or []
        self._removed = {package.base: package for package in removed}

        failed = failed or []
        self._failed = {package.base: package for package in failed}

    @property
    def failed(self) -> list[Package]:
        """
        get list of failed packages

        Returns:
            list[Package]: list of packages which were failed
        """
        return list(self._failed.values())

    @property
    def is_empty(self) -> bool:
        """
        get if build result is empty or not

        Returns:
            bool: ``True`` in case if success list is empty and ``False`` otherwise
        """
        return not self._added and not self._updated

    @property
    def removed(self) -> list[Package]:
        """
        get list of removed packages

        Returns:
            list[Package]: list of packages successfully removed
        """
        return list(self._removed.values())

    @property
    def success(self) -> list[Package]:
        """
        get list of success builds

        Returns:
            list[Package]: list of packages with success result
        """
        return list(self._added.values()) + list(self._updated.values())

    def add_added(self, package: Package) -> None:
        """
        add new package to new packages list

        Args:
            package(Package): package removed
        """
        self._added[package.base] = package

    def add_failed(self, package: Package) -> None:
        """
        add new package to failed built

        Args:
            package(Package): package with errors during build
        """
        self._failed[package.base] = package

    def add_removed(self, package: Package) -> None:
        """
        add new package to removed list

        Args:
            package(Package): package removed
        """
        self._removed[package.base] = package

    def add_updated(self, package: Package) -> None:
        """
        add new package to success built

        Args:
            package(Package): package built
        """
        self._updated[package.base] = package

    # pylint: disable=protected-access
    def merge(self, other: Result) -> Self:
        """
        merge other result into this one. This method assumes that other has fresh info about status and override it

        Args:
            other(Result): instance of the newest result

        Returns:
            Self: updated instance
        """
        for status in self.STATUS_PRIORITIES:
            new_packages: Iterable[Package] = getattr(other, f"_{status}", {}).values()
            insert_package: Callable[[Package], None] = getattr(self, f"add_{status}")
            for package in new_packages:
                insert_package(package)

        return self.refine()

    def refine(self) -> Self:
        """
        merge packages between different results (e.g. remove failed from added, etc.) removing duplicates

        Returns:
            Self: updated instance
        """
        for index, base_status in enumerate(self.STATUS_PRIORITIES):
            # extract top-level packages
            base_packages: Iterable[str] = getattr(self, f"_{base_status}", {}).keys()
            # extract packages for each bottom-level
            for status in self.STATUS_PRIORITIES[index + 1:]:
                packages: dict[str, Package] = getattr(self, f"_{status}", {})

                # if there is top-level package in bottom-level, then remove it
                for base in base_packages:
                    if base in packages:
                        del packages[base]

        return self

    # required for tests at least
    def __eq__(self, other: Any) -> bool:
        """
        check if other is the same object

        Args:
            other(Any): other object instance

        Returns:
            bool: ``True`` if the other object is the same and ``False`` otherwise
        """
        if not isinstance(other, Result):
            return False
        return self._added == other._added \
            and self._removed == other._removed \
            and self._updated == other._updated \
            and self._failed == other._failed
