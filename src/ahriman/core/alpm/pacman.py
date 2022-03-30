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
from pyalpm import Handle  # type: ignore
from typing import Set

from ahriman.core.configuration import Configuration


class Pacman:
    """
    alpm wrapper
    :ivar handle: pyalpm root `Handle`
    """

    def __init__(self, configuration: Configuration) -> None:
        """
        default constructor
        :param configuration: configuration instance
        """
        root = configuration.get("alpm", "root")
        pacman_root = configuration.getpath("alpm", "database")
        self.handle = Handle(root, str(pacman_root))
        for repository in configuration.getlist("alpm", "repositories"):
            self.handle.register_syncdb(repository, 0)  # 0 is pgp_level

    def all_packages(self) -> Set[str]:
        """
        get list of packages known for alpm
        :return: list of package names
        """
        result: Set[str] = set()
        for database in self.handle.get_syncdbs():
            for package in database.pkgcache:
                result.add(package.name)  # package itself
                result.update(package.provides)  # provides list for meta-packages

        return result
