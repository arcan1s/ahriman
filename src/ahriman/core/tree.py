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

import itertools

from typing import Callable, Iterable, List, Tuple

from ahriman.models.package import Package


class Leaf:
    """
    tree leaf implementation

    Attributes:
        dependencies(Set[str]): list of package dependencies
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
        leaves[List[Leaf]): list of tree leaves

    Examples:
        The most important feature here is to generate tree levels one by one which can be achieved by using class
        method::

            >>> from ahriman.core.configuration import Configuration
            >>> from ahriman.core.database import SQLite
            >>> from ahriman.core.repository import Repository
            >>>
            >>> configuration = Configuration()
            >>> database = SQLite.load(configuration)
            >>> repository = Repository.load("x86_64", configuration, database, report=True, unsafe=False)
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

    def __init__(self, leaves: List[Leaf]) -> None:
        """
        default constructor

        Args:
            leaves(List[Leaf]): leaves to build the tree
        """
        self.leaves = leaves

    @staticmethod
    def resolve(packages: Iterable[Package]) -> List[List[Package]]:
        """
        resolve dependency tree

        Args:
            packages(Iterable[Package]): packages list

        Returns:
            List[List[Package]]: list of packages lists based on their dependencies
        """
        leaves = [Leaf(package) for package in packages]
        instance = Tree(leaves)
        return instance.levels()

    def levels(self) -> List[List[Package]]:
        """
        get build levels starting from the packages which do not require any other package to build

        Returns:
            List[List[Package]]: sorted list of packages lists based on their dependencies
        """
        # https://docs.python.org/dev/library/itertools.html#itertools-recipes
        def partition(source: List[Leaf]) -> Tuple[List[Leaf], Iterable[Leaf]]:
            first_iter, second_iter = itertools.tee(source)
            filter_fn: Callable[[Leaf], bool] = lambda leaf: leaf.is_dependency(next_level)
            # materialize first list and leave second as iterator
            return list(filter(filter_fn, first_iter)), itertools.filterfalse(filter_fn, second_iter)

        unsorted: List[List[Leaf]] = []

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
            unsorted[current_num], to_be_moved = partition(current_level)
            unsorted[next_num].extend(to_be_moved)

        comparator: Callable[[Package], str] = lambda package: package.base
        return [
            sorted([leaf.package for leaf in level], key=comparator)
            for level in unsorted if level
        ]
