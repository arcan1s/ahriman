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
from ahriman.core.alpm.pacman import Pacman
from ahriman.core.alpm.remote import Official
from ahriman.models.aur_package import AURPackage


class OfficialSyncdb(Official):
    """
    official repository wrapper based on synchronized databases.

    Despite the fact that official repository provides an API for the interaction according to the comment in issue
    https://github.com/arcan1s/ahriman/pull/59#issuecomment-1106412297 we might face rate limits while requesting
    updates.

    This approach also has limitations, because we don't require superuser rights (neither going to download database
    separately), the database file might be outdated and must be handled manually (or kind of). This behaviour might be
    changed in the future.

    Still we leave search function based on the official repositories RPC.
    """

    def package_info(self, package_name: str, *, pacman: Pacman) -> AURPackage:
        """
        get package info by its name

        Args:
            package_name(str): package name to search
            pacman(Pacman): alpm wrapper instance

        Returns:
            AURPackage: package which match the package name
        """
        return next(AURPackage.from_pacman(package) for package in pacman.package_get(package_name))
