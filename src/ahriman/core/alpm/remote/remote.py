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

import logging

from typing import Dict, List, Type

from ahriman.models.aur_package import AURPackage


class Remote:
    """
    base class for remote package search

    Attributes:
      logger(logging.Logger): class logger
    """

    def __init__(self) -> None:
        """
        default constructor
        """
        self.logger = logging.getLogger("build_details")

    @classmethod
    def info(cls: Type[Remote], package_name: str) -> AURPackage:
        """
        get package info by its name

        Args:
          package_name(str): package name to search

        Returns:
          AURPackage: package which match the package name
        """
        return cls().package_info(package_name)

    @classmethod
    def multisearch(cls: Type[Remote], *keywords: str) -> List[AURPackage]:
        """
        search in remote repository by using API with multiple words. This method is required in order to handle
        https://bugs.archlinux.org/task/49133. In addition, short words will be dropped

        Args:
          *keywords(str): search terms, e.g. "ahriman", "is", "cool"

        Returns:
          List[AURPackage]: list of packages each of them matches all search terms
        """
        instance = cls()
        packages: Dict[str, AURPackage] = {}
        for term in filter(lambda word: len(word) > 3, keywords):
            portion = instance.search(term)
            packages = {
                package.name: package  # not mistake to group them by name
                for package in portion
                if package.name in packages or not packages
            }
        return list(packages.values())

    @classmethod
    def search(cls: Type[Remote], *keywords: str) -> List[AURPackage]:
        """
        search package in AUR web

        Args:
          *keywords(str): search terms, e.g. "ahriman", "is", "cool"

        Returns:
          List[AURPackage]: list of packages which match the criteria
        """
        return cls().package_search(*keywords)

    def package_info(self, package_name: str) -> AURPackage:
        """
        get package info by its name

        Args:
          package_name(str): package name to search

        Returns:
          AURPackage: package which match the package name

        Raises:
          NotImplementedError: not implemented method
        """
        raise NotImplementedError

    def package_search(self, *keywords: str) -> List[AURPackage]:
        """
        search package in AUR web

        Args:
          *keywords(str): keywords to search

        Returns:
          List[AURPackage]: list of packages which match the criteria

        Raises:
          NotImplementedError: not implemented method
        """
        raise NotImplementedError
