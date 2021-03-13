#
# Copyright (c) 2021 Evgenii Alekseev.
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

from typing import Iterable, List, Set

from ahriman.core.build_tools.task import Task
from ahriman.models.package import Package


class Tree:

    def __init__(self) -> None:
        self.packages: List[Leaf] = []

    def levels(self) -> List[List[Package]]:
        result: List[List[Package]] = []

        unprocessed = [leaf for leaf in self.packages]
        while unprocessed:
            result.append([leaf.package for leaf in unprocessed if leaf.is_root(unprocessed)])
            unprocessed = [leaf for leaf in unprocessed if not leaf.is_root(unprocessed)]

        return result

    def load(self, packages: Iterable[Package]) -> None:
        for package in packages:
            leaf = Leaf(package)
            leaf.load_dependencies()
            self.packages.append(leaf)


class Leaf:

    def __init__(self, package: Package) -> None:
        self.package = package
        self.dependencies: Set[str] = set()

    @property
    def items(self) -> Iterable[str]:
        return self.package.packages.keys()

    def is_root(self, packages: Iterable[Leaf]) -> bool:
        '''
        :param packages:
        :return: true if any of packages is dependency of the leaf, false otherwise
        '''
        for leaf in packages:
            if self.dependencies.intersection(leaf.items):
                return False
        return True

    def load_dependencies(self) -> None:
        clone_dir = tempfile.mkdtemp()
        try:
            Task.fetch(clone_dir, self.package.git_url)
            self.dependencies = Package.dependencies(clone_dir)
        finally:
            shutil.rmtree(clone_dir, ignore_errors=True)