#
# Copyright (c) 2021-2026 ahriman team.
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
import itertools
import shutil
import tarfile

from collections.abc import Generator, Iterable
from functools import cached_property
from pathlib import Path
from pyalpm import DB, Handle, Package, SIG_DATABASE_OPTIONAL, SIG_PACKAGE_OPTIONAL  # type: ignore[import-not-found]
from string import Template

from ahriman.core.alpm.pacman_database import PacmanDatabase
from ahriman.core.configuration import Configuration
from ahriman.core.log import LazyLogging
from ahriman.core.utils import trim_package
from ahriman.models.pacman_synchronization import PacmanSynchronization
from ahriman.models.repository_id import RepositoryId


class Pacman(LazyLogging):
    """
    alpm wrapper

    Attributes:
        configuration(Configuration): configuration instance
        refresh_database(PacmanSynchronization): synchronize local cache to remote
        repository_id(RepositoryId): repository unique identifier
        repository_paths(RepositoryPaths): repository paths instance
    """

    def __init__(self, repository_id: RepositoryId, configuration: Configuration, *,
                 refresh_database: PacmanSynchronization) -> None:
        """
        Args:
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
            refresh_database(PacmanSynchronization): synchronize local cache to remote
        """
        self.configuration = configuration
        self.repository_id = repository_id
        self.repository_paths = configuration.repository_paths

        self.refresh_database = refresh_database

    @cached_property
    def handle(self) -> Handle:
        """
        pyalpm handle

        Returns:
            Handle: generated pyalpm handle instance
        """
        return self.__create_handle(refresh_database=self.refresh_database)

    def __create_handle(self, *, refresh_database: PacmanSynchronization) -> Handle:
        """
        create lazy handle function

        Args:
            refresh_database(PacmanSynchronization): synchronize local cache to remote

        Returns:
            Handle: fully initialized pacman handle
        """
        pacman_root = self.configuration.getpath("alpm", "database")
        use_ahriman_cache = self.configuration.getboolean("alpm", "use_ahriman_cache")

        database_path = self.repository_paths.pacman if use_ahriman_cache else pacman_root
        root = self.configuration.getpath("alpm", "root")
        handle = Handle(str(root), str(database_path))

        for repository in self.configuration.getlist("alpm", "repositories"):
            database = self.database_init(handle, repository, self.repository_id.architecture)
            self.database_copy(handle, database, pacman_root, use_ahriman_cache=use_ahriman_cache)

        # install repository database too (without copying)
        self.database_init(handle, self.repository_id.name, self.repository_id.architecture)

        if use_ahriman_cache and refresh_database:
            self.database_sync(handle, force=refresh_database == PacmanSynchronization.Force)

        return handle

    def database_copy(self, handle: Handle, database: DB, pacman_root: Path, *, use_ahriman_cache: bool) -> None:
        """
        copy database from the operating system root to the ahriman local home

        Args:
            handle(Handle): pacman handle which will be used for database copying
            database(DB): pacman database instance to be copied
            pacman_root(Path): operating system pacman root
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
        dst.parent.mkdir(mode=0o755, exist_ok=True)  # create sync directory if it doesn't exist

        src = repository_database(pacman_root)
        if not src.is_file():
            self.logger.warning("repository %s is set to be used, however, no working copy was found", database.name)
            return  # database for some reason deos not exist

        self.logger.info("copy pacman database %s from operating system root to ahriman's home %s", src, dst)
        with self.repository_paths.preserve_owner(dst.parent):
            shutil.copy(src, dst)

    def database_init(self, handle: Handle, repository: str, architecture: str) -> DB:
        """
        create database instance from pacman handler and set its properties

        Args:
            handle(Handle): pacman handle which will be used for database initializing
            repository(str): pacman repository name (e.g. core)
            architecture(str): repository architecture

        Returns:
            DB: loaded pacman database instance
        """
        self.logger.info("loading pacman database %s", repository)
        database: DB = handle.register_syncdb(repository, SIG_DATABASE_OPTIONAL | SIG_PACKAGE_OPTIONAL)

        if repository != self.repository_id.name:
            mirror = self.configuration.get("alpm", "mirror")
            # replace variables in mirror address
            variables = {
                "arch": architecture,
                "repo": repository,
            }
            server = Template(mirror).safe_substitute(variables)
        else:
            # special case, same database, use local storage instead
            server = f"file://{self.repository_paths.repository}"

        database.servers = [server]

        return database

    def database_sync(self, handle: Handle, *, force: bool) -> None:
        """
        sync local database

        Args:
            handle(Handle): pacman handle which will be used for database sync
            force(bool): force database synchronization (same as ``pacman -Syy``)
        """
        self.logger.info("refresh ahriman's home pacman database (force refresh %s)", force)
        transaction = handle.init_transaction()
        for database in handle.get_syncdbs():
            PacmanDatabase(database, self.configuration).sync(force=force)
        transaction.release()

    def files(self, packages: Iterable[str]) -> dict[str, set[str]]:
        """
        extract list of known packages from the databases

        Args:
            packages(Iterable[str]): filter by package names

        Returns:
            dict[str, set[str]]: map of package name to its list of files
        """
        def extract(tar: tarfile.TarFile, versions: dict[str, str]) -> Generator[tuple[str, set[str]], None, None]:
            for package_name, version in versions.items():
                path = Path(f"{package_name}-{version}") / "files"
                try:
                    content = tar.extractfile(str(path))
                except KeyError:
                    # in case if database and its files has been desync somehow, the extractfile will raise
                    # KeyError because the entry doesn't exist
                    content = None
                if content is None:
                    continue

                # this is just array of files, however, the directories are with trailing slash,
                # which previously has been removed by the conversion to ``pathlib.Path``
                files = {filename.decode("utf8").rstrip().removesuffix("/") for filename in content.readlines()}
                yield package_name, files

        # sort is required for the following group by operation
        descriptors = sorted(
            (package for package_name in packages for package in self.package(package_name)),
            key=lambda package: package.db.name
        )

        result: dict[str, set[str]] = {}
        for database_name, pacman_packages in itertools.groupby(descriptors, lambda package: package.db.name):
            database_file = self.repository_paths.pacman / "sync" / f"{database_name}.files.tar.gz"
            if not database_file.is_file():
                continue  # no database file found

            package_names = {package.name: package.version for package in pacman_packages}
            with tarfile.open(database_file, "r:gz") as archive:
                result.update(extract(archive, package_names))

        return result

    def package(self, package_name: str) -> Generator[Package, None, None]:
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

    def packages(self) -> set[str]:
        """
        get list of packages known for alpm

        Returns:
            set[str]: list of package names
        """
        result: set[str] = set()
        for database in self.handle.get_syncdbs():
            for package in database.pkgcache:
                # package itself
                result.add(package.name)
                # provides list for meta-packages
                result.update(trim_package(provides) for provides in package.provides)

        return result

    def provided_by(self, package_name: str) -> Generator[Package, None, None]:
        """
        search through databases and emit packages which provides the ``package_name``

        Args:
            package_name(str): package name to search

        Yields:
            Package: list of packages which were returned by the query
        """
        def is_package_provided(package: Package) -> bool:
            provides = [trim_package(name) for name in package.provides]
            return package_name in provides

        for database in self.handle.get_syncdbs():
            yield from filter(is_package_provided, database.search(package_name))
