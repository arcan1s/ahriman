#
# Copyright (c) 2021-2024 ahriman team.
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

from ahriman.application.application import Application
from ahriman.application.handlers.handler import Handler
from ahriman.core.configuration import Configuration
from ahriman.models.build_status import BuildStatusEnum
from ahriman.models.package import Package
from ahriman.models.package_source import PackageSource
from ahriman.models.repository_id import RepositoryId


class Copy(Handler):
    """
    copy packages handler
    """

    ALLOW_MULTI_ARCHITECTURE_RUN = False  # conflicting action

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

        configuration_path, _ = configuration.check_loaded()
        source_repository_id = RepositoryId(repository_id.architecture, args.source)
        source_configuration = Configuration.from_path(configuration_path, source_repository_id)
        source_application = Application(source_repository_id, source_configuration, report=report)

        packages = source_application.repository.packages(args.package)
        Copy.check_status(args.exit_code, packages)

        for package in packages:
            Copy.copy_package(package, application, source_application)

        # run update
        application.update([])

        if args.remove:
            source_application.remove(args.package)

    @staticmethod
    def copy_package(package: Package, application: Application, source_application: Application) -> None:
        """
        copy package ``package`` from source repository to target repository

        Args:
            package(Package): package to copy
            application(Application): application instance of the target repository
            source_application(Application): application instance of the source repository
        """
        # copy files
        source_paths = [
            str(source_application.repository.paths.repository / source.filename)
            for source in package.packages.values()
            if source.filename is not None
        ]
        application.add(source_paths, PackageSource.Archive)

        # copy metadata
        application.reporter.package_changes_update(
            package.base, source_application.reporter.package_changes_get(package.base)
        )
        application.reporter.package_dependencies_update(
            package.base, source_application.reporter.package_dependencies_get(package.base)
        )
        application.reporter.package_update(package, BuildStatusEnum.Pending)
