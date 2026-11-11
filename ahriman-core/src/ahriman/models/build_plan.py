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
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Self

from ahriman.models.package import Package


class BuildPlanReason(StrEnum):
    """
    reason why package was selected for a build plan

    Attributes:
        BrokenImplicitDependency(BuildPlanReason): package has a broken implicit dependency
        LocalSourceUpdate(BuildPlanReason): locally sourced package has an update
        PreBuilt(BuildPlanReason): package has already been built
        QueuedRequest(BuildPlanReason): package was manually queued
        Rebuild(BuildPlanReason): package was selected for rebuild
        RegularUpdate(BuildPlanReason): package has an AUR update
        RequiredBy(BuildPlanReason): package is required by another selected package
    """

    BrokenImplicitDependency = "broken implicit dependency"
    LocalSourceUpdate = "local source update"
    PreBuilt = "pre-built"
    QueuedRequest = "queued request"
    Rebuild = "rebuild"
    RegularUpdate = "regular update"
    RequiredBy = "required by"


@dataclass(frozen=True)
class BuildPlanItem:
    """
    one package and the reason it appears in a build plan

    Attributes:
        package(Package): package selected for the plan
        reason(BuildPlanReason): why the package was selected
        requester(str | None): package that requires this package
    """

    package: Package
    reason: BuildPlanReason
    requester: str | None = None


class BuildPlan(Iterable[Package]):
    """
    in-memory preview of the packages selected for a build operation
    """

    def __init__(self) -> None:
        """
        initialize an empty build plan
        """
        self._items: dict[str, BuildPlanItem] = {}

    @property
    def items(self) -> list[BuildPlanItem]:
        """
        get plan items in stable package-base order

        Returns:
            list[BuildPlanItem]: selected plan items
        """
        return [self._items[base] for base in sorted(self._items)]

    @property
    def packages(self) -> list[Package]:
        """
        get packages in stable package-base order

        Returns:
            list[Package]: selected packages
        """
        return [item.package for item in self.items]

    def add(self, package: Package, reason: BuildPlanReason, requester: str | None = None) -> BuildPlanItem:
        """
        add or update a package in the plan

        Args:
            package(Package): package selected for the plan
            reason(BuildPlanReason): reason for selecting it
            requester(str | None, optional): package requiring this dependency (Default value = None)

        Returns:
            BuildPlanItem: plan item for the package
        """
        item = self._items[package.base] = BuildPlanItem(package, reason, requester)
        return item

    def item(self, package_base: str) -> BuildPlanItem:
        """
        get a plan item by package base

        Args:
            package_base(str): package base to look up

        Returns:
            BuildPlanItem: matching item
        """
        return self._items[package_base]

    def update(self, packages: list[Package], reason: BuildPlanReason, requester: str | None = None) -> Self:
        """
        bulk update packages with the same reason

        Args:
            packages(list[Package]): list of new packages to be added
            reason(BuildPlanReason): reason for selecting them
            requester(str | None, optional): package requiring these dependencies (Default value = None)

        Returns:
            Self: updated plan instance
        """
        for package in packages:
            self.add(package, reason, requester)
        return self

    def __contains__(self, item: Package) -> bool:
        """
        check whether plan holds a package or not

        Args:
            item(Package): package to lookup

        Returns:
            bool: ``True`` in case if the package is already in the plan and ``False`` otherwise
        """
        return item.base in self._items

    def __eq__(self, other: Any) -> bool:
        """
        check if other is the same object

        Args:
            other(Any): other object instance

        Returns:
            bool: ``True`` if the other object is the same and ``False`` otherwise
        """
        if not isinstance(other, BuildPlan):
            return False
        return self.items == other.items

    def __iter__(self) -> Iterator[Package]:
        """
        iterate over selected packages in stable package-base order

        Returns:
            Package: selected package
        """
        return iter(self.packages)

    def __len__(self) -> int:
        """
        get number of selected packages

        Returns:
            int: number of selected packages
        """
        return len(self._items)
