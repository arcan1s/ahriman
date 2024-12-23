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
from __future__ import annotations

from collections.abc import Iterable
from functools import partial

from ahriman.core.exceptions import PartitionError
from ahriman.core.utils import minmax, partition
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
            bool: ``True`` in case if package is dependency of others and ``False`` otherwise
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
            bool: ``True`` if any of packages is dependency of the leaf, ``False`` otherwise
        """
        for leaf in packages:
            if self.dependencies.intersection(leaf.items):
                return False
        return True


class Tree:
    """
    dependency tree implementation

    Attributes:
        leaves(list[Leaf]): list of tree leaves

    Examples:
        The most important feature here is to generate tree levels one by one which can be achieved by using class
        method::

            >>> from ahriman.core.configuration import Configuration
            >>> from ahriman.core.database import SQLite
            >>> from ahriman.core.repository import Repository
            >>> from ahriman.models.repository_id import RepositoryId
            >>>
            >>> configuration = Configuration()
            >>> database = SQLite.load(configuration)
            >>> repository = Repository.load(RepositoryId("x86_64", "aur"), configuration, database, report=True)
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
        Args:
            leaves(list[Leaf]): leaves to build the tree
        """
        self.leaves = leaves

    @staticmethod
    def balance(partitions: list[list[Leaf]]) -> list[list[Leaf]]:
        """
        balance partitions. This method tries to find the longest and the shortest lists and move free leaves between
        them if possible. In case if there are no free packages (i.e. the ones which don't depend on any other in
        partition and are not dependency of any), it will drop it as it is. This method is guaranteed to produce the
        same unsorted sequences for same unsorted input

        Args:
            partitions(list[list[Leaf]]): source unbalanced partitions

        Returns:
            list[list[Leaf]]: balanced partitions
        """
        # to make sure that we will have same sequences after balance we need to ensure that list is sorted
        partitions = [
            sorted(part, key=lambda leaf: leaf.package.base)
            for part in partitions if part
        ]
        if not partitions:  # nothing to balance
            return partitions

        while True:
            min_part, max_part = minmax(partitions, key=len)
            if len(max_part) - len(min_part) <= 1:  # there is nothing to balance
                break

            # find first package from max list which is not dependency and doesn't depend on any other package
            free_index = next(
                (
                    index
                    for index, leaf in enumerate(max_part)
                    if not leaf.is_dependency(max_part) and leaf.is_root(max_part)
                ),
                None
            )
            if free_index is None:  # impossible to balance between the shortest and the longest
                break

            min_part.append(max_part.pop(free_index))

        return partitions

    @staticmethod
    def partition(packages: Iterable[Package], *, count: int) -> list[list[Package]]:
        """
        partition tree into independent chunks of more or less equal amount of packages. The packages in produced
        partitions don't depend on any package from other partitions

        Args:
            packages(Iterable[Package]): packages list
            count(int): maximal amount of partitions

        Returns:
            list[list[Package]]: list of packages lists based on their dependencies. The amount of elements in each
            sublist is less or equal to ``count``

        Raises:
            PartitionError: in case if it is impossible to divide tree by specified amount of partitions
        """
        if count < 1:
            raise PartitionError(count)

        # special case
        if count == 1:
            return [sorted(packages, key=lambda package: package.base)]

        leaves = [Leaf(package) for package in packages]
        instance = Tree(leaves)
        return instance.partitions(count=count)

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

    @staticmethod
    def sort(leaves: list[list[Leaf]]) -> list[list[Package]]:
        """
        sort given list of leaves by package base

        Args:
            leaves(list[list[Leaf]]): leaves to sort

        Returns:
            list[list[Package]]: sorted list of packages on each level
        """
        return [
            sorted([leaf.package for leaf in level], key=lambda package: package.base)
            for level in leaves if level
        ]

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
            # additional workaround with partial in order to hide cell-var-from-loop pylint warning
            predicate = partial(Leaf.is_root, packages=unprocessed)
            new_level, unprocessed = partition(unprocessed, predicate)
            unsorted.append(new_level)

        # move leaves to the end if they are not required at the next level
        for current_num, current_level in enumerate(unsorted[:-1]):
            next_num = current_num + 1
            next_level = unsorted[next_num]

            # change lists inside the collection
            predicate = partial(Leaf.is_dependency, packages=next_level)
            unsorted[current_num], to_be_moved = partition(current_level, predicate)
            unsorted[next_num].extend(to_be_moved)

        return self.sort(unsorted)

    def partitions(self, *, count: int) -> list[list[Package]]:
        """
        partition tree into (more or less) equal chunks of packages which don't depend on each other

        Args:
            count(int): maximal amount of partitions

        Returns:
            list[list[Package]]: sorted list of packages partitions
        """
        unsorted: list[list[Leaf]] = [[] for _ in range(count)]

        # in order to keep result stable we will need to sort packages all times
        unprocessed = sorted(self.leaves, key=lambda leaf: leaf.package.base)
        while unprocessed:
            # pick one and append it to the most free partition and build chunk
            first_leaf = unprocessed.pop()
            chunk = [first_leaf]

            while True:  # python doesn't allow to use walrus operator to unpack tuples
                # get packages which depend on packages in chunk
                predicate = partial(Leaf.is_root, packages=chunk)
                unprocessed, new_dependent = partition(unprocessed, predicate)
                chunk.extend(new_dependent)

                # get packages which are dependency of packages in chunk
                predicate = partial(Leaf.is_dependency, packages=chunk)
                new_dependencies, unprocessed = partition(unprocessed, predicate)
                chunk.extend(new_dependencies)

                if not new_dependent and not new_dependencies:
                    break

            part = min(unsorted, key=len)
            part.extend(chunk)

        balanced = self.balance(unsorted)
        return self.sort(balanced)
