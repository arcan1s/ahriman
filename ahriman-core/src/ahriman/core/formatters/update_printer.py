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
from collections.abc import Iterator

from ahriman.core.formatters.string_printer import StringPrinter
from ahriman.core.tree import Tree
from ahriman.core.utils import full_version, parse_version
from ahriman.models.build_plan import BuildPlan
from ahriman.models.package import Package
from ahriman.models.property import Property


class UpdatePrinter(StringPrinter):
    """
    print content of the packages update

    Attributes:
        plan(BuildPlan): plan to display
        local_versions(dict[str, str]): published package versions indexed by base
        bump_pkgrel(bool): whether duplicate package releases are expected to increment
    """

    def __init__(self, plan: BuildPlan, local_versions: dict[str, str], *, bump_pkgrel: bool = True) -> None:
        """
        Args:
            plan(BuildPlan): plan to display
            local_versions(dict[str, str]): published package versions indexed by base
            bump_pkgrel(bool, optional): whether duplicate package releases are expected to increment
                (Default value = True)
        """
        StringPrinter.__init__(self, "Build plan" if plan else "No packages selected")
        self.plan = plan
        self.local_versions = local_versions
        self.bump_pkgrel = bump_pkgrel

    def properties(self) -> list[Property]:
        """
        convert content into printable data

        Returns:
            list[Property]: list of content properties
        """
        return [
            prop
            for level in Tree.resolve(self.plan)
            for package in level
            for prop in self.properties_package(package)
        ]

    def properties_package(self, package: Package) -> Iterator[Property]:
        """
        generate list of properties for the specific package

        Args:
            package(Package): package object

        Yields:
            Property: list of properties belonging to the package
        """
        # package header
        yield Property(package.base, "", is_required=True)

        # set version update message
        local_version, remote_version = self.versions(package)
        yield Property(local_version, remote_version, is_required=True, indent=2, separator=" -> ")

        # set reason
        item = self.plan.item(package.base)
        reason = item.reason.value if item.requester is None else f"{item.reason} {item.requester}"
        yield Property("Reason", reason, indent=2)

    def versions(self, package: Package) -> tuple[str, str]:
        """
        generate version property

        Returns:
            tuple[str, str]: extract current and updated versions for the package
        """
        local_version = self.local_versions.get(package.base)

        if self.bump_pkgrel and (pkgrel := package.next_pkgrel(local_version)) is not None:
            epoch, pkgver, _ = parse_version(package.version)
            effective_new_version = full_version(epoch, pkgver, pkgrel)
        else:
            effective_new_version = package.version

        return local_version or "N/A", effective_new_version
