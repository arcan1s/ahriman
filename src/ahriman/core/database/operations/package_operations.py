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
from collections.abc import Generator, Iterable
from sqlite3 import Connection

from ahriman.core.database.operations import Operations
from ahriman.models.build_status import BuildStatus
from ahriman.models.package import Package
from ahriman.models.package_description import PackageDescription
from ahriman.models.remote_source import RemoteSource


class PackageOperations(Operations):
    """
    package operations
    """

    def _package_remove_package_base(self, connection: Connection, package_base: str) -> None:
        """
        remove package base information

        Args:
            connection(Connection): database connection
            package_base(str): package base name
        """
        connection.execute(
            """
            delete from package_statuses
            where package_base = :package_base and repository = :repository and architecture = :architecture
            """,
            {
                "package_base": package_base,
                "repository": self.repository_id.name,
                "architecture": self.repository_id.architecture,
            })
        connection.execute(
            """
            delete from package_bases
            where package_base = :package_base and repository = :repository  and architecture = :architecture
            """,
            {
                "package_base": package_base,
                "repository": self.repository_id.name,
                "architecture": self.repository_id.architecture,
            })

    def _package_remove_packages(self, connection: Connection, package_base: str,
                                 current_packages: Iterable[str]) -> None:
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
                """
                select package, repository, architecture from packages
                where package_base = :package_base and repository = :repository and architecture = :architecture""",
                {
                    "package_base": package_base,
                    "repository": self.repository_id.name,
                    "architecture": self.repository_id.architecture,
                })
            if package["package"] not in current_packages
        ]
        connection.executemany(
            """
            delete from packages
            where package = :package and repository = :repository and architecture = :architecture
            """,
            packages)

    def _package_update_insert_base(self, connection: Connection, package: Package) -> None:
        """
        insert base package into table

        Args:
            connection(Connection): database connection
            package(Package): package properties
        """
        connection.execute(
            """
            insert into package_bases
            (package_base, version, source, branch, git_url, path, web_url, packager,
            repository, architecture)
            values
            (:package_base, :version, :source, :branch, :git_url, :path, :web_url, :packager,
            :repository, :architecture)
            on conflict (package_base, architecture, repository) do update set
            version = :version, branch = :branch, git_url = :git_url, path = :path, web_url = :web_url,
            source = :source, packager = :packager
            """,
            {
                "package_base": package.base,
                "version": package.version,
                "branch": package.remote.branch,
                "git_url": package.remote.git_url,
                "path": package.remote.path,
                "web_url": package.remote.web_url,
                "source": package.remote.source.value,
                "packager": package.packager,
                "repository": self.repository_id.name,
                "architecture": self.repository_id.architecture,
            }
        )

    def _package_update_insert_packages(self, connection: Connection, package: Package) -> None:
        """
        insert packages into table

        Args:
            connection(Connection): database connection
            package(Package): package properties
        """
        package_list = []
        for name, description in package.packages.items():
            if description.architecture is None:
                continue  # architecture is required
            package_list.append({
                "package": name,
                "package_base": package.base,
                "repository": self.repository_id.name,
                **description.view(),
            })
        connection.executemany(
            """
            insert into packages
            (package, package_base, architecture, archive_size,
            build_date, depends, description, filename,
            "groups", installed_size, licenses, provides,
            url, make_depends, opt_depends, check_depends,
            repository)
            values
            (:package, :package_base, :architecture, :archive_size,
            :build_date, :depends, :description, :filename,
            :groups, :installed_size, :licenses, :provides,
            :url, :make_depends, :opt_depends, :check_depends,
            :repository)
            on conflict (package, architecture, repository) do update set
            package_base = :package_base, archive_size = :archive_size,
            build_date = :build_date, depends = :depends, description = :description, filename = :filename,
            "groups" = :groups, installed_size = :installed_size, licenses = :licenses, provides = :provides,
            url = :url, make_depends = :make_depends, opt_depends = :opt_depends, check_depends = :check_depends
            """,
            package_list)

    def _package_update_insert_status(self, connection: Connection, package_base: str, status: BuildStatus) -> None:
        """
        insert base package status into table

        Args:
            connection(Connection): database connection
            package_base(str): package base name
            status(BuildStatus): new build status
        """
        connection.execute(
            """
            insert into package_statuses
            (package_base, status, last_updated, repository, architecture)
            values
            (:package_base, :status, :last_updated, :repository, :architecture)
            on conflict (package_base, architecture, repository) do update set
            status = :status, last_updated = :last_updated
            """,
            {
                "package_base": package_base,
                "status": status.status.value,
                "last_updated": status.timestamp,
                "repository": self.repository_id.name,
                "architecture": self.repository_id.architecture,
            })

    def _packages_get_select_package_bases(self, connection: Connection) -> dict[str, Package]:
        """
        select package bases from the table

        Args:
            connection(Connection): database connection

        Returns:
            dict[str, Package]: map of the package base to its descriptor (without packages themselves)
        """
        return {
            row["package_base"]: Package(
                base=row["package_base"],
                version=row["version"],
                remote=RemoteSource.from_json(row),
                packages={},
                packager=row["packager"] or None,
            ) for row in connection.execute(
                """select * from package_bases where repository = :repository and architecture = :architecture""",
                {"repository": self.repository_id.name, "architecture": self.repository_id.architecture}
            )
        }

    def _packages_get_select_packages(self, connection: Connection, packages: dict[str, Package]) -> dict[str, Package]:
        """
        select packages from the table

        Args:
            connection(Connection): database connection
            packages(dict[str, Package]): packages descriptor map

        Returns:
            dict[str, Package]: map of the package base to its descriptor including individual packages
        """
        for row in connection.execute(
                """select * from packages where repository = :repository and architecture = :architecture""",
                {"repository": self.repository_id.name, "architecture": self.repository_id.architecture}
        ):
            if row["package_base"] not in packages:
                continue  # normally must never happen though
            packages[row["package_base"]].packages[row["package"]] = PackageDescription.from_json(row)
        return packages

    def _packages_get_select_statuses(self, connection: Connection) -> dict[str, BuildStatus]:
        """
        select package build statuses from the table

        Args:
            connection(Connection): database connection

        Returns:
            dict[str, BuildStatus]: map of the package base to its status
        """
        return {
            row["package_base"]: BuildStatus.from_json({"status": row["status"], "timestamp": row["last_updated"]})
            for row in connection.execute(
                """select * from package_statuses where repository = :repository and architecture = :architecture""",
                {"repository": self.repository_id.name, "architecture": self.repository_id.architecture}
            )
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

    def packages_get(self) -> list[tuple[Package, BuildStatus]]:
        """
        get package list and their build statuses from database

        Return:
            list[tuple[Package, BuildStatus]]: list of package properties and their statuses
        """
        def run(connection: Connection) -> Generator[tuple[Package, BuildStatus], None, None]:
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

    def remotes_get(self) -> dict[str, RemoteSource]:
        """
        get packages remotes based on current settings

        Returns:
            dict[str, RemoteSource]: map of package base to its remote sources
        """
        packages = self.with_connection(self._packages_get_select_package_bases)
        return {
            package_base: package.remote
            for package_base, package in packages.items()
        }
