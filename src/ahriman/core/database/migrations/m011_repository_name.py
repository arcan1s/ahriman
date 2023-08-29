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
from sqlite3 import Connection

from ahriman.core.configuration import Configuration


__all__ = ["migrate_data", "steps"]


steps = [
    # set correct types for schema
    """
    alter table users rename to users_
    """,
    """
    create table users (
        username text not null unique,
        access text not null,
        password text,
        packager_id text,
        key_id text
    )
    """,
    """
    insert into users select * from users_
    """,
    """
    drop table users_
    """,
    # update base tables
    # build_queue
    """
    alter table build_queue add column repository text not null default ''
    """,
    """
    alter table build_queue add column architecture text not null default ''
    """,
    """
    alter table build_queue rename to build_queue_
    """,
    """
    create table build_queue (
        package_base text not null,
        properties json not null,
        repository text not null,
        architecture text not null,
        unique (package_base, architecture, repository)
    )
    """,
    """
    insert into build_queue select * from build_queue_
    """,
    """
    drop table build_queue_
    """,
    # package_bases
    """
    alter table package_bases add column repository text not null default ''
    """,
    """
    alter table package_bases add column architecture text not null default ''
    """,
    """
    alter table package_bases rename to package_bases_
    """,
    """
    create table package_bases (
        package_base text not null,
        version text not null,
        branch text,
        git_url text,
        path text,
        web_url text,
        source text,
        packager text,
        repository text not null,
        architecture text not null,
        unique (package_base, architecture, repository)
    )
    """,
    """
    insert into package_bases select * from package_bases_
    """,
    """
    drop table package_bases_
    """,
    # package_statuses
    """
    alter table package_statuses add column repository text not null default ''
    """,
    """
    alter table package_statuses add column architecture text not null default ''
    """,
    """
    alter table package_statuses rename to package_statuses_
    """,
    """
    create table package_statuses (
        package_base text not null,
        status text not null,
        last_updated integer,
        repository text not null,
        architecture text not null,
        unique (package_base, architecture, repository)
    )
    """,
    """
    insert into package_statuses select * from package_statuses_
    """,
    """
    drop table package_statuses_
    """,
    # packages
    """
    alter table packages add column repository text not null default ''
    """,
    """
    alter table packages rename to packages_
    """,
    """
    create table packages (
        package text not null,
        package_base text not null,
        architecture text not null,
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
        make_depends json,
        opt_depends json,
        check_depends json,
        repository text not null,
        unique (package, architecture, repository)
    )
    """,
    """
    insert into packages select * from packages_
    """,
    """
    drop table packages_
    """,
    # logs
    """
    alter table logs add column repository text not null default ''
    """,
    """
    alter table logs add column architecture text not null default ''
    """,
    """
    drop index logs_package_base_version
    """,
    """
    alter table logs rename to logs_
    """,
    """
    create table logs (
        package_base text not null,
        created real not null,
        record text,
        version text not null,
        repository text not null,
        architecture text not null
    )
    """,
    """
    insert into logs select * from logs_
    """,
    """
    create index logs_package_base_version_architecture_repository
    on logs (package_base, version, architecture, repository)
    """,
    """
    drop table logs_
    """,
]


def migrate_data(connection: Connection, configuration: Configuration) -> None:
    """
    perform data migration

    Args:
        connection(Connection): database connection
        configuration(Configuration): configuration instance
    """
    migrate_package_repository(connection, configuration)


def migrate_package_repository(connection: Connection, configuration: Configuration) -> None:
    """
    update repository name from current settings

    Args:
        connection(Connection): database connection
        configuration(Configuration): configuration instance
    """
    _, repository_id = configuration.check_loaded()

    connection.execute("""update build_queue set repository = :repository, architecture = :architecture""",
                       {"repository": repository_id.name, "architecture": repository_id.architecture})
    connection.execute("""update package_bases set repository = :repository, architecture = :architecture""",
                       {"repository": repository_id.name, "architecture": repository_id.architecture})
    connection.execute("""update package_statuses set repository = :repository, architecture = :architecture""",
                       {"repository": repository_id.name, "architecture": repository_id.architecture})
    connection.execute("""update packages set repository = :repository""",
                       {"repository": repository_id.name})
    connection.execute("""update logs set repository = :repository, architecture = :architecture""",
                       {"repository": repository_id.name, "architecture": repository_id.architecture})
