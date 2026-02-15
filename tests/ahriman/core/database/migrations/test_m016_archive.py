import pytest

from dataclasses import replace
from pathlib import Path
from pytest_mock import MockerFixture
from sqlite3 import Connection
from typing import Any
from unittest.mock import call as MockCall

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.configuration import Configuration
from ahriman.core.database.migrations.m016_archive import migrate_data, move_packages
from ahriman.models.package import Package
from ahriman.models.repository_paths import RepositoryPaths


def test_migrate_data(connection: Connection, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must perform data migration
    """
    _, repository_id = configuration.check_loaded()
    repositories = [
        repository_id,
        replace(repository_id, architecture="i686"),
    ]
    mocker.patch("ahriman.core.repository.Explorer.repositories_extract", return_value=repositories)
    migration_mock = mocker.patch("ahriman.core.database.migrations.m016_archive.move_packages")

    migrate_data(connection, configuration)
    migration_mock.assert_has_calls([
        MockCall(replace(configuration.repository_paths, repository_id=repository), pytest.helpers.anyvar(int))
        for repository in repositories
    ])


def test_move_packages(repository_paths: RepositoryPaths, pacman: Pacman, package_ahriman: Package,
                       mocker: MockerFixture) -> None:
    """
    must move packages to the archive directory
    """

    def is_file(self: Path, *args: Any, **kwargs: Any) -> bool:
        return "file" in self.name

    mocker.patch("pathlib.Path.iterdir", return_value=[
        repository_paths.repository / ".hidden-file.pkg.tar.xz",
        repository_paths.repository / "directory",
        repository_paths.repository / "file.pkg.tar.xz",
        repository_paths.repository / "file.pkg.tar.xz.sig",
        repository_paths.repository / "file2.pkg.tar.xz",
        repository_paths.repository / "symlink.pkg.tar.xz",
    ])
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("pathlib.Path.is_file", autospec=True, side_effect=is_file)
    mocker.patch("pathlib.Path.exists", return_value=True)
    archive_mock = mocker.patch("ahriman.models.package.Package.from_archive", return_value=package_ahriman)
    move_mock = mocker.patch("ahriman.core.database.migrations.m016_archive.atomic_move")
    symlink_mock = mocker.patch("pathlib.Path.symlink_to")

    move_packages(repository_paths, pacman)
    archive_mock.assert_has_calls([
        MockCall(repository_paths.repository / filename, pacman)
        for filename in ("file.pkg.tar.xz", "file2.pkg.tar.xz")
    ])
    move_mock.assert_has_calls([
        MockCall(repository_paths.repository / filename, repository_paths.archive_for(package_ahriman.base) / filename)
        for filename in ("file.pkg.tar.xz", "file.pkg.tar.xz.sig", "file2.pkg.tar.xz")
    ])
    symlink_mock.assert_has_calls([
        MockCall(
            Path("..") /
            ".." /
            ".." /
            repository_paths.archive_for(package_ahriman.base).relative_to(repository_paths.root) /
            filename
        )
        for filename in ("file.pkg.tar.xz", "file.pkg.tar.xz.sig", "file2.pkg.tar.xz")
    ])
