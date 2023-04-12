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
import pkg_resources
import sys

from ahriman import version
from ahriman.application.handlers import Handler
from ahriman.core.configuration import Configuration
from ahriman.core.formatters import VersionPrinter


class Versions(Handler):
    """
    version handler
    """

    ALLOW_AUTO_ARCHITECTURE_RUN = False  # it should be called only as "no-architecture"

    @classmethod
    def run(cls: type[Handler], args: argparse.Namespace, architecture: str, configuration: Configuration, *,
            report: bool, unsafe: bool) -> None:
        """
        callback for command line

        Args:
            args(argparse.Namespace): command line args
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
            report(bool): force enable or disable reporting
            unsafe(bool): if set no user check will be performed before path creation
        """
        VersionPrinter(f"Module version {version.__version__}",
                       {"Python": sys.version}).print(verbose=False, separator=" ")
        packages = Versions.package_dependencies("ahriman", ("pacman", "s3", "web"))
        VersionPrinter("Installed packages", packages).print(verbose=False, separator=" ")

    @staticmethod
    def package_dependencies(root: str, root_extras: tuple[str, ...] = ()) -> dict[str, str]:
        """
        extract list of ahriman package dependencies installed into system with their versions

        Args:
            root(str): root package name
            root_extras(tuple[str, ...], optional): extras for the root package (Default value = ())

        Returns:
            dict[str, str]: map of installed dependency to its version
        """
        resources: dict[str, pkg_resources.Distribution] = pkg_resources.working_set.by_key  # type: ignore

        def dependencies_by_key(key: str, extras: tuple[str, ...] = ()) -> list[str]:
            return [entry.key for entry in resources[key].requires(extras)]

        keys: list[str] = []
        portion = {key for key in dependencies_by_key(root, root_extras) if key in resources}
        while portion:
            keys.extend(portion)
            portion = {
                key
                for key in sum((dependencies_by_key(key) for key in portion), start=[])
                if key not in keys and key in resources
            }

        return {
            resource.project_name: resource.version
            for resource in map(lambda key: resources[key], keys)
        }
