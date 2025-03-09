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
import argparse

from collections.abc import Callable, Iterable
from dataclasses import fields
from typing import ClassVar

from ahriman.application.handlers.handler import Handler, SubParserAction
from ahriman.core.alpm.remote import AUR, Official
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import OptionError
from ahriman.core.formatters import AurPrinter
from ahriman.models.aur_package import AURPackage
from ahriman.models.repository_id import RepositoryId


class Search(Handler):
    """
    packages search handler

    Attributes:
        SORT_FIELDS(set[str]): (class attribute) allowed fields to sort the package list
    """

    ALLOW_MULTI_ARCHITECTURE_RUN = False  # system-wide action
    SORT_FIELDS: ClassVar[set[str]] = {
        field.name
        for field in fields(AURPackage)
        if field.default_factory is not list
    }

    @classmethod
    def run(cls, args: argparse.Namespace, repository_id: RepositoryId, configuration: Configuration, *,
            report: bool) -> None:
        """
        callback for command line

        Args:
            args(argparse.Namespace): command line args
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
            report(bool): force enable or disable reporting
        """
        official_packages_list = Official.multisearch(*args.search)
        aur_packages_list = AUR.multisearch(*args.search)
        non_empty = bool(official_packages_list or aur_packages_list)
        Search.check_status(args.exit_code, non_empty)

        for packages_list in (official_packages_list, aur_packages_list):
            # keep sorting by packages source
            for package in Search.sort(packages_list, args.sort_by):
                AurPrinter(package)(verbose=args.info)

    @staticmethod
    def _set_aur_search_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for AUR search subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("aur-search", aliases=["search"], help="search for package",
                                 description="search for package in AUR using API")
        parser.add_argument("search",
                            help="search terms, can be specified multiple times, the result will match all terms",
                            nargs="+")
        parser.add_argument("-e", "--exit-code", help="return non-zero exit status if result is empty",
                            action="store_true")
        parser.add_argument("--info", help="show additional package information",
                            action=argparse.BooleanOptionalAction, default=False)
        parser.add_argument("--sort-by",
                            help="sort field by this field. In case if two packages have the same value of "
                                 "the specified field, they will be always sorted by name",
                            default="name", choices=sorted(Search.SORT_FIELDS))
        parser.set_defaults(architecture="", lock=None, quiet=True, report=False, repository="", unsafe=True)
        return parser

    @staticmethod
    def sort(packages: Iterable[AURPackage], sort_by: str) -> list[AURPackage]:
        """
        sort package list by specified field

        Args:
            packages(Iterable[AURPackage]): packages list to sort
            sort_by(str): AUR package field name to sort by

        Returns:
            list[AURPackage]: sorted list for packages

        Raises:
            OptionError: if search fields is not in list of allowed ones
        """
        if sort_by not in Search.SORT_FIELDS:
            raise OptionError(sort_by)
        # always sort by package name at the last
        # well technically it is not a string, but we can deal with it
        comparator: Callable[[AURPackage], tuple[str, str]] =\
            lambda package: (getattr(package, sort_by), package.name)
        return sorted(packages, key=comparator)

    arguments = [_set_aur_search_parser]
