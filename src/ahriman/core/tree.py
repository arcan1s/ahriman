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
from __future__ import annotations

import functools

from collections.abc import Callable, Iterable

from ahriman.core.util import partition
from ahriman.models.package import Package


class Leaf:
    """
    tree leaf implementation

    Attributes:
        dependencies(set[str]): list of package dependencies
        package(Package): leaf package properties
    """

    def __init__(self, package: Package) -> None:
        """
        default constructor

        Args:
            package(Package): package properties
        """
        self.package = package
        self.dependencies = package.depends_build

    @property
    def items(self) -> Iterable[str]:
        """
        extract all packages from the leaf

        Returns:
            Iterable[str]: packages containing in this leaf
        """
        return self.package.packages.keys()

    def is_dependency(self, packages: Iterable[Leaf]) -> bool:
        """
        check if the package is dependency of any other package from list or not

        Args:
            packages(Iterable[Leaf]): list of known leaves

        Returns:
            bool: True in case if package is dependency of others and False otherwise
        """
        for leaf in packages:
            if leaf.dependencies.intersection(self.items):
                return True
        return False

    def is_root(self, packages: Iterable[Leaf]) -> bool:
        """
        check if package depends on any other package from list of not

        Args:
            packages(Iterable[Leaf]): list of known leaves

        Returns:
            bool: True if any of packages is dependency of the leaf, False otherwise
        """
        for leaf in packages:
            if self.dependencies.intersection(leaf.items):
                return False
        return True


class Tree:
    """
    dependency tree implementation

    Attributes:
        leaves[list[Leaf]): list of tree leaves

    Examples:
        The most important feature here is to generate tree levels one by one which can be achieved by using class
        method::

            >>> from ahriman.core.configuration import Configuration
            >>> from ahriman.core.database import SQLite
            >>> from ahriman.core.repository import Repository
            >>>
            >>> configuration = Configuration()
            >>> database = SQLite.load(configuration)
            >>> repository = Repository.load("x86_64", configuration, database, report=True)
            >>> packages = repository.packages()
            >>>
            >>> tree = Tree.resolve(packages)
            >>> for tree_level in tree:
            >>>     for package in tree_level:
            >>>         print(package.base)
            >>>     print()

        The direct constructor call is also possible but requires tree leaves to be instantioned in advance, e.g.::

            >>> leaves = [Leaf(package) for package in packages]
            >>> tree = Tree(leaves)
    """

    def __init__(self, leaves: list[Leaf]) -> None:
        """
        default constructor

        Args:
            leaves(list[Leaf]): leaves to build the tree
        """
        self.leaves = leaves

    @staticmethod
    def resolve(packages: Iterable[Package]) -> list[list[Package]]:
        """
        resolve dependency tree

        Args:
            packages(Iterable[Package]): packages list

        Returns:
            list[list[Package]]: list of packages lists based on their dependencies
        """
        leaves = [Leaf(package) for package in packages]
        instance = Tree(leaves)
        return instance.levels()

    def levels(self) -> list[list[Package]]:
        """
        get build levels starting from the packages which do not require any other package to build

        Returns:
            list[list[Package]]: sorted list of packages lists based on their dependencies
        """
        unsorted: list[list[Leaf]] = []

        # build initial tree
        unprocessed = self.leaves[:]
        while unprocessed:
            unsorted.append([leaf for leaf in unprocessed if leaf.is_root(unprocessed)])
            unprocessed = [leaf for leaf in unprocessed if not leaf.is_root(unprocessed)]

        # move leaves to the end if they are not required at the next level
        for current_num, current_level in enumerate(unsorted[:-1]):
            next_num = current_num + 1
            next_level = unsorted[next_num]

            # change lists inside the collection
            # additional workaround with partial in order to hide cell-var-from-loop pylint warning
            predicate = functools.partial(Leaf.is_dependency, packages=next_level)
            unsorted[current_num], to_be_moved = partition(current_level, predicate)
            unsorted[next_num].extend(to_be_moved)

        comparator: Callable[[Package], str] = lambda package: package.base
        return [
            sorted([leaf.package for leaf in level], key=comparator)
            for level in unsorted if level
        ]
