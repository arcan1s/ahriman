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
import sys

from pathlib import Path

from ahriman.application.application import Application
from ahriman.application.handlers.handler import Handler, SubParserAction
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
    def _set_patch_add_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for new single-function patch subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("patch-add", help="add patch for PKGBUILD function",
                                 description="create or update patched PKGBUILD function or variable",
                                 epilog="Unlike ``patch-set-add``, this function allows to patch only one PKGBUILD "
                                        "function, e.g. typing ``ahriman patch-add ahriman pkgver`` it will change the "
                                        "``pkgver`` inside PKGBUILD, typing ``ahriman patch-add ahriman build()`` "
                                        "it will change ``build()`` function inside PKGBUILD.")
        parser.add_argument("package", help="package base")
        parser.add_argument("variable", help="PKGBUILD variable or function name. If variable is a function, "
                                             "it must end with ()")
        parser.add_argument("patch", help="path to file which contains function or variable value. If not set, "
                                          "the value will be read from stdin", type=Path, nargs="?")
        parser.set_defaults(action=Action.Update, architecture="", exit_code=False, lock=None, report=False,
                            repository="")
        return parser

    @staticmethod
    def _set_patch_list_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for list patches subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("patch-list", help="list patch sets",
                                 description="list available patches for the package")
        parser.add_argument("package", help="package base")
        parser.add_argument("-e", "--exit-code", help="return non-zero exit status if result is empty",
                            action="store_true")
        parser.add_argument("-v", "--variable", help="if set, show only patches for specified PKGBUILD variables",
                            action="append")
        parser.set_defaults(action=Action.List, architecture="", lock=None, report=False, repository="", unsafe=True)
        return parser

    @staticmethod
    def _set_patch_remove_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for remove patches subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("patch-remove", help="remove patch set", description="remove patches for the package")
        parser.add_argument("package", help="package base")
        parser.add_argument("-v", "--variable",
                            help="should be used for single-function patches in case if you wold like "
                                 "to remove only specified PKGBUILD variables. In case if not set, "
                                 "it will remove all patches related to the package",
                            action="append")
        parser.set_defaults(action=Action.Remove, architecture="", exit_code=False, lock=None, report=False,
                            repository="")
        return parser

    @staticmethod
    def _set_patch_set_add_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for new full-diff patch subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("patch-set-add", help="add patch set", description="create or update source patches",
                                 epilog="In order to add a patch set for the package you will need to:\n\n"
                                        "1. Clone the AUR package manually.\n"
                                        "2. Add required changes (e.g. external patches, edit PKGBUILD).\n"
                                        "3. Run command, e.g. ``ahriman patch-set-add path/to/directory``.\n\n"
                                        "By default it tracks ``*.patch`` and ``*.diff`` files, but this behavior "
                                        "can be changed by using ``--track`` option.")
        parser.add_argument("package", help="path to directory with changed files for patch addition/update", type=Path)
        parser.add_argument("-t", "--track", help="files which has to be tracked", action="append",
                            default=["*.diff", "*.patch"])
        parser.set_defaults(action=Action.Update, architecture="", exit_code=False, lock=None, report=False,
                            repository="", variable=None)
        return parser

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
            # pylint: disable=bad-builtin
            print("Post new function or variable value below. Press Ctrl-D to finish:", file=sys.stderr)
            patch = "".join(list(sys.stdin))
        else:
            patch = patch_path.read_text(encoding="utf8")
        # remove spaces around the patch and parse to correct type
        return PkgbuildPatch.parse(variable, patch.strip())

    @staticmethod
    def patch_set_create(application: Application, package_base: str, patch: PkgbuildPatch) -> None:
        """
        create patch set for the package base

        Args:
            application(Application): application instance
            package_base(str): package base
            patch(PkgbuildPatch): patch descriptor
        """
        application.reporter.package_patches_update(package_base, patch)

    @staticmethod
    def patch_set_list(application: Application, package_base: str, variables: list[str] | None,
                       exit_code: bool) -> None:
        """
        list patches available for the package base

        Args:
            application(Application): application instance
            package_base(str): package base
            variables(list[str] | None): extract patches only for specified PKGBUILD variables
            exit_code(bool): exit with error on empty search result
        """
        patches = [
            patch
            for patch in application.reporter.package_patches_get(package_base, None)
            if variables is None or patch.key in variables
        ]
        Patch.check_status(exit_code, patches)

        PatchPrinter(package_base, patches)(verbose=True, separator=" = ")

    @staticmethod
    def patch_set_remove(application: Application, package_base: str, variables: list[str] | None) -> None:
        """
        remove patch set for the package base

        Args:
            application(Application): application instance
            package_base(str): package base
            variables(list[str] | None): remove patches only for specified PKGBUILD variables
        """
        if variables is not None:
            for variable in variables:  # iterate over single variable
                application.reporter.package_patches_remove(package_base, variable)
        else:
            application.reporter.package_patches_remove(package_base, None)  # just pass as is

    arguments = [
        _set_patch_add_parser,
        _set_patch_list_parser,
        _set_patch_remove_parser,
        _set_patch_set_add_parser,
    ]
