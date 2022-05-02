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
import json

from sqlite3 import Connection

from ahriman.models.build_status import BuildStatus
from ahriman.models.package import Package
from ahriman.models.repository_paths import RepositoryPaths


__all__ = ["migrate_package_statuses"]


def migrate_package_statuses(connection: Connection, paths: RepositoryPaths) -> None:
    """
    perform migration for package statuses

    Args:
        connection(Connection): database connection
        paths(RepositoryPaths): repository paths instance
    """
    def insert_base(metadata: Package, last_status: BuildStatus) -> None:
        connection.execute(
            """
            insert into package_bases
            (package_base, version, aur_url)
            values
            (:package_base, :version, :aur_url)
            """,
            dict(package_base=metadata.base, version=metadata.version, aur_url=""))
        connection.execute(
            """
            insert into package_statuses
            (package_base, status, last_updated)
            values
            (:package_base, :status, :last_updated)""",
            dict(package_base=metadata.base, status=last_status.status.value, last_updated=last_status.timestamp))

    def insert_packages(metadata: Package) -> None:
        package_list = []
        for name, description in metadata.packages.items():
            package_list.append(dict(package=name, package_base=metadata.base, **description.view()))
        connection.executemany(
            """
            insert into packages
            (package, package_base, architecture, archive_size, build_date, depends, description,
            filename, "groups", installed_size, licenses, provides, url)
            values
            (:package, :package_base, :architecture, :archive_size, :build_date, :depends, :description,
            :filename, :groups, :installed_size, :licenses, :provides, :url)
            """,
            package_list)

    cache_path = paths.root / "status_cache.json"
    if not cache_path.is_file():
        return  # no file found
    with cache_path.open() as cache:
        dump = json.load(cache)

    for item in dump.get("packages", []):
        package = Package.from_json(item["package"])
        status = BuildStatus.from_json(item["status"])
        insert_base(package, status)
        insert_packages(package)
