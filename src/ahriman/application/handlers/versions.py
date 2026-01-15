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
import re
import sys

from collections.abc import Iterator
from importlib import metadata
from typing import ClassVar

from ahriman import __version__
from ahriman.application.handlers.handler import Handler, SubParserAction
from ahriman.core.configuration import Configuration
from ahriman.core.formatters import VersionPrinter
from ahriman.models.repository_id import RepositoryId


class Versions(Handler):
    """
    version handler

    Attributes:
        PEP423_PACKAGE_NAME(re.Pattern[str]): (class attribute) special regex for valid PEP423 package name
    """

    ALLOW_MULTI_ARCHITECTURE_RUN = False  # system-wide action
    PEP423_PACKAGE_NAME: ClassVar[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9._-]+")

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
        VersionPrinter(f"Module version {__version__}",
                       {"Python": sys.version})(verbose=False, separator=" ")
        packages = Versions.package_dependencies("ahriman")
        VersionPrinter("Installed packages", dict(packages))(verbose=False, separator=" ")

    @staticmethod
    def _set_help_version_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for version subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("help-version", aliases=["version"], help="application version",
                                 description="print application and its dependencies versions")
        parser.set_defaults(architecture="", lock=None, quiet=True, report=False, repository="", unsafe=True)
        return parser

    @staticmethod
    def package_dependencies(root: str) -> Iterator[tuple[str, str]]:
        """
        extract list of ahriman package dependencies installed into system with their versions

        Args:
            root(str): root package name

        Yields:
            tuple[str, str]: map of installed dependency to its version
        """
        def dependencies_by_key(key: str) -> Iterator[str]:
            # in importlib it returns requires in the following format
            # ["pytest (>=3.0.0) ; extra == 'test'", "pytest-cov ; extra == 'test'"]
            try:
                requires = metadata.requires(key)
            except metadata.PackageNotFoundError:
                return
            for entry in requires or []:
                yield from Versions.PEP423_PACKAGE_NAME.findall(entry)

        keys: list[str] = []
        portion = set(dependencies_by_key(root))
        while portion:
            keys.extend(portion)
            portion = {
                key
                for key in sum((list(dependencies_by_key(key)) for key in portion), start=[])
                if key not in keys
            }

        for key in keys:
            try:
                distribution = metadata.distribution(key)
                yield distribution.name, distribution.version
            except metadata.PackageNotFoundError:
                continue

    arguments = [_set_help_version_parser]
