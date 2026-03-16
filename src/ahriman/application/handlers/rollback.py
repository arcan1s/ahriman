#
# Copyright (c) 2021-2026 ahriman team.
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

from dataclasses import replace
from pathlib import Path

from ahriman.application.application import Application
from ahriman.application.handlers.add import Add
from ahriman.application.handlers.handler import Handler, SubParserAction
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import UnknownPackageError
from ahriman.core.utils import extract_user
from ahriman.models.package import Package
from ahriman.models.package_source import PackageSource
from ahriman.models.repository_id import RepositoryId


class Rollback(Handler):
    """
    package rollback handler
    """

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
        application = Application(repository_id, configuration, report=report)
        application.on_start()

        package = Rollback.package_load(application, args.package, args.version)
        artifacts = Rollback.package_artifacts(application, package)

        args.package = [str(artifact) for artifact in artifacts]
        Add.perform_action(application, args)

        if args.hold:
            application.reporter.package_hold_update(package.base, enabled=True)

    @staticmethod
    def _set_package_rollback_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for package rollback subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("package-rollback", help="rollback package",
                                 description="rollback package to specified version from archives")
        parser.add_argument("package", help="package base")
        parser.add_argument("version", help="package version")
        parser.add_argument("--hold", help="hold package afterwards",
                            action=argparse.BooleanOptionalAction, default=True)
        parser.add_argument("-u", "--username", help="build as user", default=extract_user())
        parser.set_defaults(aur=False, changes=False, check_files=False, dependencies=False, dry_run=False,
                            exit_code=True, increment=False, now=True, local=False, manual=False, refresh=False,
                            source=PackageSource.Archive, variable=None, vcs=False)
        return parser

    @staticmethod
    def package_artifacts(application: Application, package: Package) -> list[Path]:
        """
        look for requested package artifacts and return paths to them

        Args:
            application(Application): application instance
            package(Package): package descriptor

        Returns:
            list[Path]: paths to found artifacts

        Raises:
            UnknownPackageError: if artifacts do not exist
        """
        # lookup for built artifacts
        artifacts = application.repository.package_archives_lookup(package)
        if not artifacts:
            raise UnknownPackageError(package.base)
        return artifacts

    @staticmethod
    def package_load(application: Application, package_base: str, version: str) -> Package:
        """
        load package from repository, while setting requested version

        Args:
            application(Application): application instance
            package_base(str): package base
            version(str): package version

        Returns:
            Package: loaded package

        Raises:
            UnknownPackageError: if package does not exist
        """
        try:
            package, _ = next(iter(application.reporter.package_get(package_base)))
            return replace(package, version=version)
        except StopIteration:
            raise UnknownPackageError(package_base) from None

    arguments = [_set_package_rollback_parser]
