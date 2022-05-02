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
from ahriman.models.remote_source import RemoteSource


class PackageOperations(Operations):
    """
    package operations
    """

    @staticmethod
    def _package_remove_package_base(connection: Connection, package_base: str) -> None:
        """
        remove package base information

        Args:
            connection(Connection): database connection
            package_base(str): package base name
        """
        connection.execute("""delete from package_statuses where package_base = :package_base""",
                           {"package_base": package_base})
        connection.execute("""delete from package_bases where package_base = :package_base""",
                           {"package_base": package_base})

    @staticmethod
    def _package_remove_packages(connection: Connection, package_base: str, current_packages: Iterable[str]) -> None:
        """
        remove packages belong to the package base

        Args:
            connection(Connection): database connection
            package_base(str): package base name
            current_packages(Iterable[str]): current packages list which has to be left in database
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

        Args:
            connection(Connection): database connection
            package(Package): package properties
        """
        connection.execute(
            """
            insert into package_bases
            (package_base, version, source, branch, git_url, path, web_url)
            values
            (:package_base, :version, :source, :branch, :git_url, :path, :web_url)
            on conflict (package_base) do update set
            version = :version, branch = :branch, git_url = :git_url, path = :path, web_url = :web_url, source = :source
            """,
            dict(
                package_base=package.base,
                version=package.version,
                branch=package.remote.branch if package.remote is not None else None,
                git_url=package.remote.git_url if package.remote is not None else None,
                path=package.remote.path if package.remote is not None else None,
                web_url=package.remote.web_url if package.remote is not None else None,
                source=package.remote.source.value if package.remote is not None else None,
            )
        )

    @staticmethod
    def _package_update_insert_packages(connection: Connection, package: Package) -> None:
        """
        insert packages into table

        Args:
            connection(Connection): database connection
            package(Package): package properties
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

        Args:
            connection(Connection): database connection
            package_base(str): package base name
            status(BuildStatus): new build status
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

        Args:
            connection(Connection): database connection

        Returns:
            Dict[str, Package]: map of the package base to its descriptor (without packages themselves)
        """
        return {
            row["package_base"]: Package(row["package_base"], row["version"], RemoteSource.from_json(row), {})
            for row in connection.execute("""select * from package_bases""")
        }

    @staticmethod
    def _packages_get_select_packages(connection: Connection, packages: Dict[str, Package]) -> Dict[str, Package]:
        """
        select packages from the table

        Args:
            connection(Connection): database connection
            packages(Dict[str, Package]): packages descriptor map

        Returns:
            Dict[str, Package]: map of the package base to its descriptor including individual packages
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

        Args:
            connection(Connection): database connection

        Returns:
            Dict[str, BuildStatus]: map of the package base to its status
        """
        return {
            row["package_base"]: BuildStatus.from_json({"status": row["status"], "timestamp": row["last_updated"]})
            for row in connection.execute("""select * from package_statuses""")
        }

    def package_remove(self, package_base: str) -> None:
        """
        remove package from database

        Args:
            package_base(str): package base name
        """
        def run(connection: Connection) -> None:
            self._package_remove_packages(connection, package_base, [])
            self._package_remove_package_base(connection, package_base)

        return self.with_connection(run, commit=True)

    def package_update(self, package: Package, status: BuildStatus) -> None:
        """
        update package status

        Args:
            package(Package): package properties
            status(BuildStatus): new build status
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

        Return:
            List[Tuple[Package, BuildStatus]]: list of package properties and their statuses
        """
        def run(connection: Connection) -> Generator[Tuple[Package, BuildStatus], None, None]:
            packages = self._packages_get_select_package_bases(connection)
            statuses = self._packages_get_select_statuses(connection)
            for package_base, package in self._packages_get_select_packages(connection, packages).items():
                yield package, statuses.get(package_base, BuildStatus())

        return self.with_connection(lambda connection: list(run(connection)))

    def remote_update(self, package: Package) -> None:
        """
        update package remote source

        Args:
            package(Package): package properties
        """
        return self.with_connection(
            lambda connection: self._package_update_insert_base(connection, package),
            commit=True)

    def remotes_get(self) -> Dict[str, RemoteSource]:
        """
        get packages remotes based on current settings

        Returns:
            Dict[str, RemoteSource]: map of package base to its remote sources
        """
        packages = self.with_connection(self._packages_get_select_package_bases)
        return {
            package_base: package.remote
            for package_base, package in packages.items()
            if package.remote is not None
        }
