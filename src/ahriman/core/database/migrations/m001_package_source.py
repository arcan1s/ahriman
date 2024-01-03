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
from sqlite3 import Connection

from ahriman.core.configuration import Configuration
from ahriman.models.package_source import PackageSource
from ahriman.models.remote_source import RemoteSource
from ahriman.models.repository_paths import RepositoryPaths


__all__ = ["migrate_data", "steps"]


steps = [
    """
    alter table package_bases add column branch text
    """,
    """
    alter table package_bases add column git_url text
    """,
    """
    alter table package_bases add column path text
    """,
    """
    alter table package_bases add column web_url text
    """,
    """
    alter table package_bases add column source text
    """,
    """
    alter table package_bases drop column aur_url
    """,
]


def migrate_data(connection: Connection, configuration: Configuration) -> None:
    """
    perform data migration

    Args:
        connection(Connection): database connection
        configuration(Configuration): configuration instance
    """
    migrate_package_remotes(connection, configuration.repository_paths)


# pylint: disable=protected-access
def migrate_package_remotes(connection: Connection, paths: RepositoryPaths) -> None:
    """
    perform migration for package remote sources

    Args:
        connection(Connection): database connection
        paths(RepositoryPaths): repository paths instance
    """
    from ahriman.core.alpm.remote import AUR
    from ahriman.models.package import Package

    def get_packages() -> dict[str, Package]:
        return {
            row["package_base"]: Package(
                base=row["package_base"],
                version=row["version"],
                remote=RemoteSource.from_json(row),
                packages={},
                packager=row.get("packager") or None,
            ) for row in connection.execute("""select * from package_bases""")
        }

    def insert_remote(base: str, remote: RemoteSource) -> None:
        connection.execute(
            """
            update package_bases set
            branch = :branch, git_url = :git_url, path = :path,
            web_url = :web_url, source = :source
            where package_base = :package_base
            """,
            {
                "package_base": base,
                "branch": remote.branch, "git_url": remote.git_url, "path": remote.path,
                "web_url": remote.web_url, "source": remote.source
            }
        )

    for package_base, package in get_packages().items():
        local_cache = paths.cache_for(package_base)
        if local_cache.exists() and not package.is_vcs:
            continue  # skip packages which are not VCS and with local cache
        remote_source = RemoteSource(
            source=PackageSource.AUR,
            git_url=AUR.remote_git_url(package_base, "aur"),
            web_url=AUR.remote_web_url(package_base),
            path=".",
            branch="master",
        )
        insert_remote(package_base, remote_source)
