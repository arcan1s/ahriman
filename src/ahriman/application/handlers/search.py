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
import argparse

from dataclasses import fields
from typing import Callable, Iterable, List, Tuple, Type

from ahriman.application.handlers.handler import Handler
from ahriman.core.alpm.remote.aur import AUR
from ahriman.core.alpm.remote.official import Official
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import InvalidOption
from ahriman.core.formatters.aur_printer import AurPrinter
from ahriman.models.aur_package import AURPackage


class Search(Handler):
    """
    packages search handler

    Attributes:
      SORT_FIELDS(Set[str]): (class attribute) allowed fields to sort the package list
    """

    ALLOW_AUTO_ARCHITECTURE_RUN = False  # it should be called only as "no-architecture"
    SORT_FIELDS = {field.name for field in fields(AURPackage) if field.default_factory is not list}

    @classmethod
    def run(cls: Type[Handler], args: argparse.Namespace, architecture: str,
            configuration: Configuration, no_report: bool, unsafe: bool) -> None:
        """
        callback for command line

        Args:
          args(argparse.Namespace): command line args
          architecture(str): repository architecture
          configuration(Configuration): configuration instance
          no_report(bool): force disable reporting
          unsafe(bool): if set no user check will be performed before path creation
        """
        official_packages_list = Official.multisearch(*args.search)
        aur_packages_list = AUR.multisearch(*args.search)
        Search.check_if_empty(args.exit_code, not official_packages_list and not aur_packages_list)

        for packages_list in (official_packages_list, aur_packages_list):
            # keep sorting by packages source
            for package in Search.sort(packages_list, args.sort_by):
                AurPrinter(package).print(args.info)

    @staticmethod
    def sort(packages: Iterable[AURPackage], sort_by: str) -> List[AURPackage]:
        """
        sort package list by specified field

        Args:
          packages(Iterable[AURPackage]): packages list to sort
          sort_by(str): AUR package field name to sort by

        Returns:
          List[AURPackage]: sorted list for packages
        """
        if sort_by not in Search.SORT_FIELDS:
            raise InvalidOption(sort_by)
        # always sort by package name at the last
        # well technically it is not a string, but we can deal with it
        comparator: Callable[[AURPackage], Tuple[str, str]] =\
            lambda package: (getattr(package, sort_by), package.name)
        return sorted(packages, key=comparator)
