#
# Copyright (c) 2021-2023 ahriman team.
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
import sys

from pathlib import Path

from ahriman.application.application import Application
from ahriman.application.handlers import Handler
from ahriman.core.build_tools.sources import Sources
from ahriman.core.configuration import Configuration
from ahriman.core.formatters import PatchPrinter
from ahriman.models.action import Action
from ahriman.models.package import Package
from ahriman.models.pkgbuild_patch import PkgbuildPatch
from ahriman.models.repository_id import RepositoryId


class Patch(Handler):
    """
    patch control handler
    """

    ALLOW_MULTI_ARCHITECTURE_RUN = False  # system-wide action

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

        match args.action:
            case Action.Update if args.variable is not None:
                patch = Patch.patch_create_from_function(args.variable, args.patch)
                Patch.patch_set_create(application, args.package, patch)
            case Action.Update:
                package_base, patch = Patch.patch_create_from_diff(args.package, repository_id.architecture, args.track)
                Patch.patch_set_create(application, package_base, patch)
            case Action.List:
                Patch.patch_set_list(application, args.package, args.variable, args.exit_code)
            case Action.Remove:
                Patch.patch_set_remove(application, args.package, args.variable)

    @staticmethod
    def patch_create_from_diff(sources_dir: Path, architecture: str, track: list[str]) -> tuple[str, PkgbuildPatch]:
        """
        create PKGBUILD plain diff patches from sources directory

        Args:
            sources_dir(Path): path to directory with the package sources
            architecture(str): repository architecture
            track(list[str]): track files which match the glob before creating the patch

        Returns:
            tuple[str, PkgbuildPatch]: package base and created PKGBUILD patch based on the diff from master HEAD
                to current files
        """
        package = Package.from_build(sources_dir, architecture, None)
        patch = Sources.patch_create(sources_dir, *track)
        return package.base, PkgbuildPatch(None, patch)

    @staticmethod
    def patch_create_from_function(variable: str, patch_path: Path | None) -> PkgbuildPatch:
        """
        create single-function patch set for the package base

        Args:
            variable(str): function or variable name inside PKGBUILD
            patch_path(Path | None): optional path to patch content. If not set, it will be read from stdin

        Returns:
            PkgbuildPatch: created patch for the PKGBUILD function
        """
        if patch_path is None:
            print("Post new function or variable value below. Press Ctrl-D to finish:", file=sys.stderr)
            patch = "".join(list(sys.stdin))
        else:
            patch = patch_path.read_text(encoding="utf8")
        patch = patch.strip()  # remove spaces around the patch
        return PkgbuildPatch(variable, patch)

    @staticmethod
    def patch_set_create(application: Application, package_base: str, patch: PkgbuildPatch) -> None:
        """
        create patch set for the package base

        Args:
            application(Application): application instance
            package_base(str): package base
            patch(PkgbuildPatch): patch descriptor
        """
        application.database.patches_insert(package_base, patch)

    @staticmethod
    def patch_set_list(application: Application, package_base: str | None, variables: list[str] | None,
                       exit_code: bool) -> None:
        """
        list patches available for the package base

        Args:
            application(Application): application instance
            package_base(str | None): package base
            variables(list[str] | None): extract patches only for specified PKGBUILD variables
            exit_code(bool): exit with error on empty search result
        """
        patches = application.database.patches_list(package_base, variables)
        Patch.check_if_empty(exit_code, not patches)

        for base, patch in patches.items():
            PatchPrinter(base, patch).print(verbose=True, separator=" = ")

    @staticmethod
    def patch_set_remove(application: Application, package_base: str, variables: list[str] | None) -> None:
        """
        remove patch set for the package base

        Args:
            application(Application): application instance
            package_base(str): package base
            variables(list[str] | None): remove patches only for specified PKGBUILD variables
        """
        application.database.patches_remove(package_base, variables)
