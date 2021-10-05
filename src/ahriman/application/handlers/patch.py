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
import shutil

from pathlib import Path
from typing import List, Type

from ahriman.application.application import Application
from ahriman.application.handlers.handler import Handler
from ahriman.core.build_tools.sources import Sources
from ahriman.core.configuration import Configuration
from ahriman.models.action import Action
from ahriman.models.package import Package


class Patch(Handler):
    """
    patch control handler
    """

    _print = print

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
        application = Application(architecture, configuration, no_report)

        if args.action == Action.List:
            Patch.patch_set_list(application, args.package)
        elif args.action == Action.Remove:
            Patch.patch_set_remove(application, args.package)
        elif args.action == Action.Update:
            Patch.patch_set_create(application, Path(args.package), args.track)

    @staticmethod
    def patch_set_create(application: Application, sources_dir: Path, track: List[str]) -> None:
        """
        create patch set for the package base
        :param application: application instance
        :param sources_dir: path to directory with the package sources
        :param track: track files which match the glob before creating the patch
        """
        package = Package.load(sources_dir, application.repository.pacman, application.repository.aur_url)
        patch_dir = application.repository.paths.patches_for(package.base)

        if patch_dir.is_dir():
            shutil.rmtree(patch_dir)  # remove old patches
        patch_dir.mkdir(mode=0o755, parents=True)

        Sources.patch_create(sources_dir, patch_dir / "00-main.patch", *track)

    @staticmethod
    def patch_set_list(application: Application, package_base: str) -> None:
        """
        list patches available for the package base
        :param application: application instance
        :param package_base: package base
        """
        patch_dir = application.repository.paths.patches_for(package_base)
        if not patch_dir.is_dir():
            return
        for patch_path in sorted(patch_dir.glob("*.patch")):
            Patch._print(patch_path.name)

    @staticmethod
    def patch_set_remove(application: Application, package_base: str) -> None:
        """
        remove patch set for the package base
        :param application: application instance
        :param package_base: package base
        """
        patch_dir = application.repository.paths.patches_for(package_base)
        shutil.rmtree(patch_dir, ignore_errors=True)
