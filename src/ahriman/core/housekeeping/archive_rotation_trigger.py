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
from collections.abc import Callable
from functools import cmp_to_key

from ahriman.core import context
from ahriman.core.alpm.pacman import Pacman
from ahriman.core.configuration import Configuration
from ahriman.core.triggers import Trigger
from ahriman.core.utils import package_like
from ahriman.models.package import Package
from ahriman.models.repository_id import RepositoryId
from ahriman.models.result import Result


class ArchiveRotationTrigger(Trigger):
    """
    remove packages from archive

    Attributes:
        keep_built_packages(int): number of last packages to keep
        paths(RepositoryPaths): repository paths instance
    """

    CONFIGURATION_SCHEMA = {
        "archive": {
            "type": "dict",
            "schema": {
                "keep_built_packages": {
                    "type": "integer",
                    "required": True,
                    "coerce": "integer",
                    "min": 0,
                },
            },
        },
    }

    def __init__(self, repository_id: RepositoryId, configuration: Configuration) -> None:
        """
        Args:
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
        """
        Trigger.__init__(self, repository_id, configuration)

        section = next(iter(self.configuration_sections(configuration)))
        self.keep_built_packages = max(configuration.getint(section, "keep_built_packages"), 0)
        self.paths = configuration.repository_paths

    @classmethod
    def configuration_sections(cls, configuration: Configuration) -> list[str]:
        """
        extract configuration sections from configuration

        Args:
            configuration(Configuration): configuration instance

        Returns:
            list[str]: read configuration sections belong to this trigger
        """
        return list(cls.CONFIGURATION_SCHEMA.keys())

    def archives_remove(self, package: Package, pacman: Pacman) -> None:
        """
        remove older versions of the specified package

        Args:
            package(Package): package which has been updated to check for older versions
            pacman(Pacman): alpm wrapper instance
        """
        packages: dict[tuple[str, str], Package] = {}
        # we can't use here load_archives, because it ignores versions
        for full_path in filter(package_like, self.paths.archive_for(package.base).iterdir()):
            local = Package.from_archive(full_path, pacman)
            packages.setdefault((local.base, local.version), local).packages.update(local.packages)

        comparator: Callable[[Package, Package], int] = lambda left, right: left.vercmp(right.version)
        to_remove = sorted(packages.values(), key=cmp_to_key(comparator))
        # 0 will imlicitly be tranlsated into [:0], meaning we keep all packages
        for single in to_remove[:-self.keep_built_packages]:
            self.logger.info("removing version %s of package %s", single.version, single.base)
            for archive in single.packages.values():
                for path in self.paths.archive_for(single.base).glob(f"{archive.filename}*"):
                    path.unlink()

    def on_result(self, result: Result, packages: list[Package]) -> None:
        """
        run trigger

        Args:
            result(Result): build result
            packages(list[Package]): list of all available packages
        """
        ctx = context.get()
        pacman = ctx.get(Pacman)

        for package in result.success:
            self.archives_remove(package, pacman)
