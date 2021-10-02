#
# Copyright (c) 2021 ahriman team.
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
import aur  # type: ignore

from typing import Callable, Type

from ahriman.application.handlers.handler import Handler
from ahriman.core.configuration import Configuration


class Search(Handler):
    """
    packages search handler
    """

    ALLOW_AUTO_ARCHITECTURE_RUN = False  # it should be called only as "no-architecture"

    @classmethod
    def run(cls: Type[Handler], args: argparse.Namespace, architecture: str,
            configuration: Configuration, no_report: bool) -> None:
        """
        callback for command line
        :param args: command line args
        :param architecture: repository architecture
        :param configuration: configuration instance
        :param no_report: force disable reporting
        """
        search = " ".join(args.search)
        packages = aur.search(search)

        # it actually always should return string
        # explicit cast to string just to avoid mypy warning for untyped library
        comparator: Callable[[aur.Package], str] = lambda item: str(item.package_base)
        for package in sorted(packages, key=comparator):
            Search.log_fn(package)

    @staticmethod
    def log_fn(package: aur.Package) -> None:
        """
        log package information
        :param package: package object as from AUR
        """
        print(f"=> {package.package_base} {package.version}")
        print(f"   {package.description}")
