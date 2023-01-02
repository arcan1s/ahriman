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
import shutil

from pathlib import Path
from pyalpm import DB, Handle, Package, SIG_PACKAGE, error as PyalpmError  # type: ignore
from typing import Any, Callable, Generator, Set

from ahriman.core.configuration import Configuration
from ahriman.core.log import LazyLogging
from ahriman.models.repository_paths import RepositoryPaths


class Pacman(LazyLogging):
    """
    alpm wrapper

    Attributes:
        handle(Handle): pyalpm root ``Handle``
    """

    handle: Handle

    def __init__(self, architecture: str, configuration: Configuration, *, refresh_database: int) -> None:
        """
        default constructor

        Args:
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
            refresh_database(int): synchronize local cache to remote. If set to ``0``, no syncronization will be
                enabled, if set to ``1`` - normal syncronization, if set to ``2`` - force syncronization
        """
        self.__create_handle_fn: Callable[[], Handle] = lambda: self.__create_handle(
            architecture, configuration, refresh_database=refresh_database)

    def __create_handle(self, architecture: str, configuration: Configuration, *, refresh_database: int) -> Handle:
        """
        create lazy handle function

        Args:
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
            refresh_database(int): synchronize local cache to remote. If set to ``0``, no syncronization will be
                enabled, if set to ``1`` - normal syncronization, if set to ``2`` - force syncronization

        Returns:
            Handle: fully initialized pacman handle
        """
        root = configuration.getpath("alpm", "root")
        pacman_root = configuration.getpath("alpm", "database")
        use_ahriman_cache = configuration.getboolean("alpm", "use_ahriman_cache")
        mirror = configuration.get("alpm", "mirror")
        paths = configuration.repository_paths
        database_path = paths.pacman if use_ahriman_cache else pacman_root

        handle = Handle(str(root), str(database_path))
        for repository in configuration.getlist("alpm", "repositories"):
            database = self.database_init(handle, repository, mirror, architecture)
            self.database_copy(handle, database, pacman_root, paths, use_ahriman_cache=use_ahriman_cache)

        if use_ahriman_cache and refresh_database:
            self.database_sync(handle, force=refresh_database > 1)

        return handle

    def database_copy(self, handle: Handle, database: DB, pacman_root: Path, paths: RepositoryPaths, *,
                      use_ahriman_cache: bool) -> None:
        """
        copy database from the operating system root to the ahriman local home

        Args:
            handle(Handle): pacman handle which will be used for database copying
            database(DB): pacman database instance to be copied
            pacman_root(Path): operating system pacman root
            paths(RepositoryPaths): repository paths instance
            use_ahriman_cache(bool): use local ahriman cache instead of system one
        """
        def repository_database(root: Path) -> Path:
            return root / "sync" / f"{database.name}.db"

        if not use_ahriman_cache:
            return
        # copy root database if no local copy found
        pacman_db_path = Path(handle.dbpath)
        if not pacman_db_path.is_dir():
            return  # root directory does not exist yet
        dst = repository_database(pacman_db_path)
        if dst.is_file():
            return  # file already exists, do not copy
        src = repository_database(pacman_root)
        if not src.is_file():
            self.logger.warning("repository %s is set to be used, however, no working copy was found", database.name)
            return  # database for some reasons deos not exist
        self.logger.info("copy pacman database from operating system root to ahriman's home")
        shutil.copy(src, dst)
        paths.chown(dst)

    def database_init(self, handle: Handle, repository: str, mirror: str, architecture: str) -> DB:
        """
        create database instance from pacman handler and set its properties

        Args:
            handle(Handle): pacman handle which will be used for database initializing
            repository(str): pacman repository name (e.g. core)
            mirror(str): arch linux mirror url
            architecture(str): repository architecture

        Returns:
            DB: loaded pacman database instance
        """
        self.logger.info("loading pacman databases")
        database: DB = handle.register_syncdb(repository, SIG_PACKAGE)
        # replace variables in mirror address
        database.servers = [mirror.replace("$repo", repository).replace("$arch", architecture)]
        return database

    def database_sync(self, handle: Handle, *, force: bool) -> None:
        """
        sync local database

        Args:
            handle(Handle): pacman handle which will be used for database sync
            force(bool): force database syncronization (same as ``pacman -Syy``)
        """
        self.logger.info("refresh ahriman's home pacman database (force refresh %s)", force)
        transaction = handle.init_transaction()
        for database in handle.get_syncdbs():
            try:
                database.update(force)
            except PyalpmError:
                self.logger.exception("exception during update %s", database.name)
        transaction.release()

    def package_get(self, package_name: str) -> Generator[Package, None, None]:
        """
        retrieve list of the packages from the repository by name

        Args:
            package_name(str): package name to search

        Yields:
            Package: list of packages which were returned by the query
        """
        for database in self.handle.get_syncdbs():
            package = database.get_pkg(package_name)
            if package is None:
                continue
            yield package

    def packages(self) -> Set[str]:
        """
        get list of packages known for alpm

        Returns:
            Set[str]: list of package names
        """
        result: Set[str] = set()
        for database in self.handle.get_syncdbs():
            for package in database.pkgcache:
                result.add(package.name)  # package itself
                result.update(package.provides)  # provides list for meta-packages

        return result

    def __getattr__(self, item: str) -> Any:
        """
        pacman handle extractor

        Args:
            item(str): property name

        Returns:
            Any: attribute by its name

        Raises:
            AttributeError: in case if no such attribute found
        """
        if item == "handle":
            handle = self.__create_handle_fn()
            setattr(self, item, handle)
            return handle
        return super().__getattr__(item)  # required for logging attribute
