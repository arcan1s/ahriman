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

from typing import Iterable, List, Set, Type

from ahriman.core.build_tools.sources import Sources
from ahriman.core.database.sqlite import SQLite
from ahriman.core.util import tmpdir
from ahriman.models.package import Package


class Leaf:
    """
    tree leaf implementation

    Attributes:
        dependencies(Set[str]): list of package dependencies
        package(Package): leaf package properties
    """

    def __init__(self, package: Package, dependencies: Set[str]) -> None:
        """
        default constructor

        Args:
            package(Package): package properties
            dependencies(Set[str]): package dependencies
        """
        self.package = package
        self.dependencies = dependencies

    @property
    def items(self) -> Iterable[str]:
        """
        extract all packages from the leaf

        Returns:
            Iterable[str]: packages containing in this leaf
        """
        return self.package.packages.keys()

    @classmethod
    def load(cls: Type[Leaf], package: Package, database: SQLite) -> Leaf:
        """
        load leaf from package with dependencies

        Args:
            package(Package): package properties
            database(SQLite): database instance

        Returns:
            Leaf: loaded class
        """
        with tmpdir() as clone_dir:
            Sources.load(clone_dir, package.remote, database.patches_get(package.base))
            dependencies = Package.dependencies(clone_dir)
        return cls(package, dependencies)

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
            >>> from ahriman.core.database.sqlite import SQLite
            >>> from ahriman.core.repository import Repository
            >>>
            >>> configuration = Configuration()
            >>> database = SQLite.load(configuration)
            >>> repository = Repository("x86_64", configuration, database, no_report=False, unsafe=False)
            >>> packages = repository.packages()
            >>>
            >>> tree = Tree.load(packages, database)
            >>> for tree_level in tree.levels():
            >>>     for package in tree_level:
            >>>         print(package.base)
            >>>     print()

        The direct constructor call is also possible but requires tree leaves to be instantioned in advance, e.g.::

            >>> leaves = [Leaf.load(package, database) for package in packages]
            >>> tree = Tree(leaves)

        Using the default ``Leaf()`` method is possible, but not really recommended because it requires from the user to
        build the dependency list by himself::

            >>> leaf = Leaf(package, dependecies)
            >>> tree = Tree([leaf])
    """

    def __init__(self, leaves: List[Leaf]) -> None:
        """
        default constructor

        Args:
            leaves(List[Leaf]): leaves to build the tree
        """
        self.leaves = leaves

    @classmethod
    def load(cls: Type[Tree], packages: Iterable[Package], database: SQLite) -> Tree:
        """
        load tree from packages

        Args:
            packages(Iterable[Package]): packages list
            database(SQLite): database instance

        Returns:
            Tree: loaded class
        """
        return cls([Leaf.load(package, database) for package in packages])

    def levels(self) -> List[List[Package]]:
        """
        get build levels starting from the packages which do not require any other package to build

        Returns:
            List[List[Package]]: list of packages lists
        """
        result: List[List[Package]] = []

        unprocessed = self.leaves[:]
        while unprocessed:
            result.append([leaf.package for leaf in unprocessed if leaf.is_root(unprocessed)])
            unprocessed = [leaf for leaf in unprocessed if not leaf.is_root(unprocessed)]

        return result
