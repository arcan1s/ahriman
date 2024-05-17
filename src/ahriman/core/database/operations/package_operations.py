#
# Copyright (c) 2021-2024 ahriman team.
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

from ahriman.core.database.operations.operations import Operations
from ahriman.models.build_status import BuildStatus
from ahriman.models.package import Package
from ahriman.models.package_description import PackageDescription
from ahriman.models.remote_source import RemoteSource
from ahriman.models.repository_id import RepositoryId


class PackageOperations(Operations):
    """
    package operations
    """

    @staticmethod
    def _package_remove_package_base(connection: Connection, package_base: str, repository_id: RepositoryId) -> None:
        """
        remove package base information

        Args:
            connection(Connection): database connection
            package_base(str): package base name
            repository_id(RepositoryId): repository unique identifier
        """
        connection.execute(
            """delete from package_statuses where package_base = :package_base and repository = :repository""",
            {"package_base": package_base, "repository": repository_id.id})
        connection.execute(
            """delete from package_bases where package_base = :package_base and repository = :repository""",
            {"package_base": package_base, "repository": repository_id.id})

    @staticmethod
    def _package_remove_packages(connection: Connection, package_base: str, current_packages: Iterable[str],
                                 repository_id: RepositoryId) -> None:
        """
        remove packages belong to the package base

        Args:
            connection(Connection): database connection
            package_base(str): package base name
            current_packages(Iterable[str]): current packages list which has to be left in database
            repository_id(RepositoryId): repository unique identifier
        """
        packages = [
            package
            for package in connection.execute(
                """
                select package, repository from packages
                where package_base = :package_base and repository = :repository""",
                {"package_base": package_base, "repository": repository_id.id})
            if package["package"] not in current_packages
        ]
        connection.executemany(
            """delete from packages where package = :package and repository = :repository""",
            packages)

    @staticmethod
    def _package_update_insert_base(connection: Connection, package: Package, repository_id: RepositoryId) -> None:
        """
        insert base package into table

        Args:
            connection(Connection): database connection
            package(Package): package properties
            repository_id(RepositoryId): repository unique identifier
        """
        connection.execute(
            """
            insert into package_bases
            (package_base, version, source, branch, git_url, path, web_url, packager, repository)
            values
            (:package_base, :version, :source, :branch, :git_url, :path, :web_url, :packager, :repository)
            on conflict (package_base, repository) do update set
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
                "repository": repository_id.id,
            }
        )

    @staticmethod
    def _package_update_insert_packages(connection: Connection, package: Package, repository_id: RepositoryId) -> None:
        """
        insert packages into table

        Args:
            connection(Connection): database connection
            package(Package): package properties
            repository_id(RepositoryId): repository unique identifier
        """
        package_list = []
        for name, description in package.packages.items():
            if description.architecture is None:
                continue  # architecture is required
            package_list.append({
                "package": name,
                "package_base": package.base,
                "repository": repository_id.id,
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

    @staticmethod
    def _packages_get_select_package_bases(connection: Connection, repository_id: RepositoryId) -> dict[str, Package]:
        """
        select package bases from the table

        Args:
            connection(Connection): database connection
            repository_id(RepositoryId): repository unique identifier

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
                """select * from package_bases where repository = :repository""",
                {"repository": repository_id.id}
            )
        }

    @staticmethod
    def _packages_get_select_packages(connection: Connection, packages: dict[str, Package],
                                      repository_id: RepositoryId) -> dict[str, Package]:
        """
        select packages from the table

        Args:
            connection(Connection): database connection
            packages(dict[str, Package]): packages descriptor map
            repository_id(RepositoryId): repository unique identifier

        Returns:
            dict[str, Package]: map of the package base to its descriptor including individual packages
        """
        for row in connection.execute(
                """select * from packages where repository = :repository""",
                {"repository": repository_id.id}
        ):
            if row["package_base"] not in packages:
                continue  # normally must never happen though
            packages[row["package_base"]].packages[row["package"]] = PackageDescription.from_json(row)
        return packages

    @staticmethod
    def _packages_get_select_statuses(connection: Connection, repository_id: RepositoryId) -> dict[str, BuildStatus]:
        """
        select package build statuses from the table

        Args:
            connection(Connection): database connection
            repository_id(RepositoryId): repository unique identifier

        Returns:
            dict[str, BuildStatus]: map of the package base to its status
        """
        return {
            row["package_base"]: BuildStatus.from_json({"status": row["status"], "timestamp": row["last_updated"]})
            for row in connection.execute(
                """select * from package_statuses where repository = :repository""",
                {"repository": repository_id.id}
            )
        }

    def package_remove(self, package_base: str, repository_id: RepositoryId | None = None) -> None:
        """
        remove package from database

        Args:
            package_base(str): package base name
            repository_id(RepositoryId, optional): repository unique identifier override (Default value = None)
        """
        repository_id = repository_id or self._repository_id

        def run(connection: Connection) -> None:
            self._package_remove_packages(connection, package_base, [], repository_id)
            self._package_remove_package_base(connection, package_base, repository_id)

        return self.with_connection(run, commit=True)

    def package_update(self, package: Package, repository_id: RepositoryId | None = None) -> None:
        """
        update package status

        Args:
            package(Package): package properties
            repository_id(RepositoryId, optional): repository unique identifier override (Default value = None)
        """
        repository_id = repository_id or self._repository_id

        def run(connection: Connection) -> None:
            self._package_update_insert_base(connection, package, repository_id)
            self._package_update_insert_packages(connection, package, repository_id)
            self._package_remove_packages(connection, package.base, package.packages.keys(), repository_id)

        return self.with_connection(run, commit=True)

    def packages_get(self, repository_id: RepositoryId | None = None) -> list[tuple[Package, BuildStatus]]:
        """
        get package list and their build statuses from database

        Args:
            repository_id(RepositoryId, optional): repository unique identifier override (Default value = None)

        Return:
            list[tuple[Package, BuildStatus]]: list of package properties and their statuses
        """
        repository_id = repository_id or self._repository_id

        def run(connection: Connection) -> Generator[tuple[Package, BuildStatus], None, None]:
            packages = self._packages_get_select_package_bases(connection, repository_id)
            statuses = self._packages_get_select_statuses(connection, repository_id)
            per_package_base = self._packages_get_select_packages(connection, packages, repository_id)
            for package_base, package in per_package_base.items():
                yield package, statuses.get(package_base, BuildStatus())

        return self.with_connection(lambda connection: list(run(connection)))

    def status_update(self, package_base: str, status: BuildStatus, repository_id: RepositoryId | None = None) -> None:
        """
        insert base package status into table

        Args:
            package_base(str): package base name
            status(BuildStatus): new build status
            repository_id(RepositoryId, optional): repository unique identifier override (Default value = None)
        """
        repository_id = repository_id or self._repository_id

        def run(connection: Connection) -> None:
            connection.execute(
                """
                insert into package_statuses
                (package_base, status, last_updated, repository)
                values
                (:package_base, :status, :last_updated, :repository)
                on conflict (package_base, repository) do update set
                status = :status, last_updated = :last_updated
                """,
                {
                    "package_base": package_base,
                    "status": status.status.value,
                    "last_updated": status.timestamp,
                    "repository": repository_id.id,
                })

        return self.with_connection(run, commit=True)
