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
from typing import Dict, Generator, Iterable, List, Tuple

from ahriman.core.database.operations.operations import Operations
from ahriman.models.build_status import BuildStatus
from ahriman.models.package import Package
from ahriman.models.package_description import PackageDescription


class PackageOperations(Operations):
    """
    package operations
    """

    @staticmethod
    def _package_remove_package_base(connection: Connection, package_base: str) -> None:
        """
        remove package base information
        :param connection: database connection
        :param package_base: package base name
        """
        connection.execute("""delete from package_statuses where package_base = :package_base""",
                           {"package_base": package_base})
        connection.execute("""delete from package_bases where package_base = :package_base""",
                           {"package_base": package_base})

    @staticmethod
    def _package_remove_packages(connection: Connection, package_base: str, current_packages: Iterable[str]) -> None:
        """
        remove packages belong to the package base
        :param connection: database connection
        :param package_base: package base name
        :param current_packages: current packages list which has to be left in database
        """
        packages = [
            package
            for package in connection.execute(
                """select package from packages where package_base = :package_base""", {"package_base": package_base})
            if package["package"] not in current_packages
        ]
        connection.executemany("""delete from packages where package = :package""", packages)

    @staticmethod
    def _package_update_insert_base(connection: Connection, package: Package) -> None:
        """
        insert base package into table
        :param connection: database connection
        :param package: package properties
        """
        connection.execute(
            """
            insert into package_bases
            (package_base, version, aur_url)
            values
            (:package_base, :version, :aur_url)
            on conflict (package_base) do update set
            version = :version, aur_url = :aur_url
            """,
            dict(package_base=package.base, version=package.version, aur_url=package.aur_url))

    @staticmethod
    def _package_update_insert_packages(connection: Connection, package: Package) -> None:
        """
        insert packages into table
        :param connection: database connection
        :param package: package properties
        """
        package_list = []
        for name, description in package.packages.items():
            package_list.append(dict(package=name, package_base=package.base, **description.view()))
        connection.executemany(
            """
            insert into packages
            (package, package_base, architecture, archive_size,
            build_date, depends, description, filename,
            "groups", installed_size, licenses, provides, url)
            values
            (:package, :package_base, :architecture, :archive_size,
            :build_date, :depends, :description, :filename,
            :groups, :installed_size, :licenses, :provides, :url)
            on conflict (package, architecture) do update set
            package_base = :package_base, archive_size = :archive_size,
            build_date = :build_date, depends = :depends, description = :description, filename = :filename,
            "groups" = :groups, installed_size = :installed_size, licenses = :licenses, provides = :provides, url = :url
            """,
            package_list)

    @staticmethod
    def _package_update_insert_status(connection: Connection, package_base: str, status: BuildStatus) -> None:
        """
        insert base package status into table
        :param connection: database connection
        :param package_base: package base name
        :param status: new build status
        """
        connection.execute(
            """
            insert into package_statuses (package_base, status, last_updated)
            values
            (:package_base, :status, :last_updated)
            on conflict (package_base) do update set
            status = :status, last_updated = :last_updated
            """,
            dict(package_base=package_base, status=status.status.value, last_updated=status.timestamp))

    @staticmethod
    def _packages_get_select_package_bases(connection: Connection) -> Dict[str, Package]:
        """
        select package bases from the table
        :param connection: database connection
        :return: map of the package base to its descriptor (without packages themselves)
        """
        return {
            row["package_base"]: Package(row["package_base"], row["version"], row["aur_url"], {})
            for row in connection.execute("""select * from package_bases""")
        }

    @staticmethod
    def _packages_get_select_packages(connection: Connection, packages: Dict[str, Package]) -> Dict[str, Package]:
        """
        select packages from the table
        :param connection: database connection
        :param packages: packages descriptor map
        :return: map of the package base to its descriptor including individual packages
        """
        for row in connection.execute("""select * from packages"""):
            if row["package_base"] not in packages:
                continue  # normally must never happen though
            packages[row["package_base"]].packages[row["package"]] = PackageDescription.from_json(row)
        return packages

    @staticmethod
    def _packages_get_select_statuses(connection: Connection) -> Dict[str, BuildStatus]:
        """
        select package build statuses from the table
        :param connection: database connection
        :return: map of the package base to its status
        """
        return {
            row["package_base"]: BuildStatus.from_json({"status": row["status"], "timestamp": row["last_updated"]})
            for row in connection.execute("""select * from package_statuses""")
        }

    def package_remove(self, package_base: str) -> None:
        """
        remove package from database
        :param package_base: package base name
        """
        def run(connection: Connection) -> None:
            self._package_remove_packages(connection, package_base, [])
            self._package_remove_package_base(connection, package_base)

        return self.with_connection(run, commit=True)

    def package_update(self, package: Package, status: BuildStatus) -> None:
        """
        update package status
        :param package: package properties
        :param status: new build status
        """
        def run(connection: Connection) -> None:
            self._package_update_insert_base(connection, package)
            self._package_update_insert_status(connection, package.base, status)
            self._package_update_insert_packages(connection, package)
            self._package_remove_packages(connection, package.base, package.packages.keys())

        return self.with_connection(run, commit=True)

    def packages_get(self) -> List[Tuple[Package, BuildStatus]]:
        """
        get package list and their build statuses from database
        :return: list of package properties and their statuses
        """
        def run(connection: Connection) -> Generator[Tuple[Package, BuildStatus], None, None]:
            packages = self._packages_get_select_package_bases(connection)
            statuses = self._packages_get_select_statuses(connection)
            for package_base, package in self._packages_get_select_packages(connection, packages).items():
                yield package, statuses.get(package_base, BuildStatus())

        return self.with_connection(lambda connection: list(run(connection)))
