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
import json

from sqlite3 import Connection

from ahriman.core.configuration import Configuration
from ahriman.models.build_status import BuildStatus
from ahriman.models.package import Package
from ahriman.models.repository_paths import RepositoryPaths


__all__ = ["migrate_data", "steps"]


steps = [
    """
    create table build_queue (
        package_base text not null unique,
        properties json not null
    )
    """,
    """
    create table package_bases (
        package_base text not null unique,
        version text not null,
        aur_url text not null
    )
    """,
    """
    create table package_statuses (
        package_base text not null unique,
        status text not null,
        last_updated integer
    )
    """,
    """
    create table packages (
        package text not null,
        package_base text not null,
        architecture text,
        archive_size integer,
        build_date integer,
        depends json,
        description text,
        filename text,
        "groups" json,
        installed_size integer,
        licenses json,
        provides json,
        url text,
        unique (package, architecture)
    )
    """,
    """
    create table patches (
        package_base text not null unique,
        patch blob not null
    )
    """,
    """
    create table users (
        username text not null unique,
        access text not null,
        password text
    )
    """,
]


def migrate_data(connection: Connection, configuration: Configuration) -> None:
    """
    perform data migration

    Args:
        connection(Connection): database connection
        configuration(Configuration): configuration instance
    """
    migrate_package_statuses(connection, configuration.repository_paths)
    migrate_patches(connection, configuration.repository_paths)
    migrate_users_data(connection, configuration)


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
            {"package_base": metadata.base, "version": metadata.version, "aur_url": ""})
        connection.execute(
            """
            insert into package_statuses
            (package_base, status, last_updated)
            values
            (:package_base, :status, :last_updated)""",
            {"package_base": metadata.base, "status": last_status.status.value, "last_updated": last_status.timestamp})

    def insert_packages(metadata: Package) -> None:
        package_list = []
        for name, description in metadata.packages.items():
            package_list.append({"package": name, "package_base": metadata.base, **description.view()})
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
    with cache_path.open(encoding="utf8") as cache:
        dump = json.load(cache)

    for item in dump.get("packages", []):
        package = Package.from_json(item["package"])
        status = BuildStatus.from_json(item["status"])
        insert_base(package, status)
        insert_packages(package)


def migrate_patches(connection: Connection, paths: RepositoryPaths) -> None:
    """
    perform migration for patches

    Args:
        connection(Connection): database connection
        paths(RepositoryPaths): repository paths instance
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


def migrate_users_data(connection: Connection, configuration: Configuration) -> None:
    """
    perform migration for users

    Args:
        connection(Connection): database connection
        configuration(Configuration): configuration instance
    """
    for section in configuration.sections():
        for option, value in configuration[section].items():
            if not section.startswith("auth:"):
                continue
            access = section[5:]
            connection.execute(
                """insert into users (username, access, password) values (:username, :access, :password)""",
                {"username": option.lower(), "access": access, "password": value})
