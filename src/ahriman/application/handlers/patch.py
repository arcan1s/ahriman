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

from pathlib import Path
from typing import List, Optional, Type

from ahriman.application.application import Application
from ahriman.application.handlers import Handler
from ahriman.core.build_tools.sources import Sources
from ahriman.core.configuration import Configuration
from ahriman.core.formatters import StringPrinter
from ahriman.models.action import Action
from ahriman.models.package import Package


class Patch(Handler):
    """
    patch control handler
    """

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
        application = Application(architecture, configuration, no_report, unsafe)

        if args.action == Action.List:
            Patch.patch_set_list(application, args.package, args.exit_code)
        elif args.action == Action.Remove:
            Patch.patch_set_remove(application, args.package)
        elif args.action == Action.Update:
            Patch.patch_set_create(application, Path(args.package), args.track)

    @staticmethod
    def patch_set_create(application: Application, sources_dir: Path, track: List[str]) -> None:
        """
        create patch set for the package base

        Args:
            application(Application): application instance
            sources_dir(Path): path to directory with the package sources
            track(List[str]): track files which match the glob before creating the patch
        """
        package = Package.from_build(sources_dir)
        patch = Sources.patch_create(sources_dir, *track)
        application.database.patches_insert(package.base, patch)

    @staticmethod
    def patch_set_list(application: Application, package_base: Optional[str], exit_code: bool) -> None:
        """
        list patches available for the package base

        Args:
            application(Application): application instance
            package_base(Optional[str]): package base
            exit_code(bool): exit with error on empty search result
        """
        patches = application.database.patches_list(package_base)
        Patch.check_if_empty(exit_code, not patches)

        for base, patch in patches.items():
            content = base if package_base is None else patch
            StringPrinter(content).print(verbose=True)

    @staticmethod
    def patch_set_remove(application: Application, package_base: str) -> None:
        """
        remove patch set for the package base

        Args:
            application(Application): application instance
            package_base(str): package base
        """
        application.database.patches_remove(package_base)
