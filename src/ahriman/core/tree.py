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

import shutil
import tempfile

from pathlib import Path
from typing import Iterable, List, Set, Type

from ahriman.core.build_tools.sources import Sources
from ahriman.core.database.sqlite import SQLite
from ahriman.models.package import Package


class Leaf:
    """
    tree leaf implementation
    :ivar dependencies: list of package dependencies
    :ivar package: leaf package properties
    """

    def __init__(self, package: Package, dependencies: Set[str]) -> None:
        """
        default constructor
        :param package: package properties
        :param dependencies: package dependencies
        """
        self.package = package
        self.dependencies = dependencies

    @property
    def items(self) -> Iterable[str]:
        """
        :return: packages containing in this leaf
        """
        return self.package.packages.keys()

    @classmethod
    def load(cls: Type[Leaf], package: Package, database: SQLite) -> Leaf:
        """
        load leaf from package with dependencies
        :param package: package properties
        :param database: database instance
        :return: loaded class
        """
        clone_dir = Path(tempfile.mkdtemp())
        try:
            Sources.load(clone_dir, package.git_url, database.patches_get(package.base))
            dependencies = Package.dependencies(clone_dir)
        finally:
            shutil.rmtree(clone_dir, ignore_errors=True)
        return cls(package, dependencies)

    def is_root(self, packages: Iterable[Leaf]) -> bool:
        """
        check if package depends on any other package from list of not
        :param packages: list of known leaves
        :return: True if any of packages is dependency of the leaf, False otherwise
        """
        for leaf in packages:
            if self.dependencies.intersection(leaf.items):
                return False
        return True


class Tree:
    """
    dependency tree implementation
    :ivar leaves: list of tree leaves
    """

    def __init__(self, leaves: List[Leaf]) -> None:
        """
        default constructor
        :param leaves: leaves to build the tree
        """
        self.leaves = leaves

    @classmethod
    def load(cls: Type[Tree], packages: Iterable[Package], database: SQLite) -> Tree:
        """
        load tree from packages
        :param packages: packages list
        :param database: database instance
        :return: loaded class
        """
        return cls([Leaf.load(package, database) for package in packages])

    def levels(self) -> List[List[Package]]:
        """
        get build levels starting from the packages which do not require any other package to build
        :return: list of packages lists
        """
        result: List[List[Package]] = []

        unprocessed = self.leaves[:]
        while unprocessed:
            result.append([leaf.package for leaf in unprocessed if leaf.is_root(unprocessed)])
            unprocessed = [leaf for leaf in unprocessed if not leaf.is_root(unprocessed)]

        return result
