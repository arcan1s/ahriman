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
from ahriman.application.handlers.handler import Handler, SubParserAction
from ahriman.core.configuration import Configuration
from ahriman.core.utils import enum_values, extract_user
from ahriman.models.package_source import PackageSource
from ahriman.models.packagers import Packagers
from ahriman.models.pkgbuild_patch import PkgbuildPatch
from ahriman.models.repository_id import RepositoryId


class Add(Handler):
    """
    add packages handler
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
        application = Application(repository_id, configuration, report=report, refresh_pacman_database=args.refresh)
        application.on_start()

        application.add(args.package, args.source, args.username)
        patches = [PkgbuildPatch.from_env(patch) for patch in args.variable] if args.variable is not None else []
        for package in args.package:  # for each requested package insert patch
            for patch in patches:
                application.reporter.package_patches_update(package, patch)

        if not args.now:
            return

        packages = application.updates(args.package, aur=False, local=False, manual=True, vcs=False, check_files=False)
        if args.changes:  # generate changes if requested
            application.changes(packages)

        packages = application.with_dependencies(packages, process_dependencies=args.dependencies)
        packagers = Packagers(args.username, {package.base: package.packager for package in packages})

        application.print_updates(packages, log_fn=application.logger.info)
        result = application.update(packages, packagers, bump_pkgrel=args.increment)
        Add.check_status(args.exit_code, not result.is_empty)

    @staticmethod
    def _set_package_add_parser(root: SubParserAction) -> argparse.ArgumentParser:
        """
        add parser for package addition subcommand

        Args:
            root(SubParserAction): subparsers for the commands

        Returns:
            argparse.ArgumentParser: created argument parser
        """
        parser = root.add_parser("package-add", aliases=["add", "package-update"], help="add package",
                                 description="add existing or new package to the build queue",
                                 epilog="This subcommand should be used for new package addition. "
                                        "It also supports flag --now in case if you would like to build "
                                        "the package immediately. You can add new package from one of "
                                        "supported sources:\n\n"
                                        "1. If it is already built package you can specify the path to the archive.\n"
                                        "2. You can also add built packages from the directory (e.g. during the "
                                        "migration from another repository source).\n"
                                        "3. It is also possible to add package from local PKGBUILD, but in this case "
                                        "it will be ignored during the next automatic updates.\n"
                                        "4. Ahriman supports downloading archives from remote (e.g. HTTP) sources.\n"
                                        "5. Finally you can add package from AUR.")
        parser.add_argument("package", help="package source (base name, path to local files, remote URL)", nargs="+")
        parser.add_argument("--changes", help="calculate changes from the latest known commit if available",
                            action=argparse.BooleanOptionalAction, default=True)
        parser.add_argument("--dependencies", help="process missing package dependencies",
                            action=argparse.BooleanOptionalAction, default=True)
        parser.add_argument("-e", "--exit-code", help="return non-zero exit status if result is empty",
                            action="store_true")
        parser.add_argument("--increment", help="increment package release (pkgrel) version on duplicate",
                            action=argparse.BooleanOptionalAction, default=True)
        parser.add_argument("-n", "--now", help="run update function after", action="store_true")
        parser.add_argument("-y", "--refresh", help="download fresh package databases from the mirror before actions, "
                                                    "-yy to force refresh even if up to date",
                            action="count", default=False)
        parser.add_argument("-s", "--source", help="explicitly specify the package source for this command",
                            type=PackageSource, choices=enum_values(PackageSource), default=PackageSource.Auto)
        parser.add_argument("-u", "--username", help="build as user", default=extract_user())
        parser.add_argument("-v", "--variable", help="apply specified makepkg variables to the next build",
                            action="append")
        return parser

    arguments = [_set_package_add_parser]
