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
from sqlite3 import Connection

from ahriman.models.repository_paths import RepositoryPaths


def migrate_patches(connection: Connection, paths: RepositoryPaths) -> None:
    """
    perform migration for patches
    :param connection: database connection
    :param paths: repository paths instance
    """
    root = paths.root / "patches"
    if not root.is_dir():
        return  # no directory found

    for package in root.iterdir():
        patch_path = package / "00-main.patch"
        if not patch_path.is_file():
            continue  # not exist
        content = patch_path.read_text(encoding="utf8")
        connection.execute(
            """insert into patches (package_base, patch) values (:package_base, :patch)""",
            {"package_base": package.name, "patch": content})

    connection.commit()
