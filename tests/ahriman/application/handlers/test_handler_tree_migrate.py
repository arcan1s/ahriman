import argparse

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.application.handlers.tree_migrate import TreeMigrate
from ahriman.core.configuration import Configuration
from ahriman.models.package import Package
from ahriman.models.repository_id import RepositoryId
from ahriman.models.repository_paths import RepositoryPaths


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    tree_create_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_create")
    application_mock = mocker.patch("ahriman.application.handlers.tree_migrate.TreeMigrate.tree_move")
    symlinks_mock = mocker.patch("ahriman.application.handlers.tree_migrate.TreeMigrate.fix_symlinks")
    _, repository_id = configuration.check_loaded()
    old_paths = configuration.repository_paths
    new_paths = RepositoryPaths(old_paths.root, old_paths.repository_id, _force_current_tree=True)

    TreeMigrate.run(args, repository_id, configuration, report=False)
    tree_create_mock.assert_called_once_with()
    application_mock.assert_called_once_with(old_paths, new_paths)
    symlinks_mock.assert_called_once_with(new_paths)


def test_fix_symlinks(repository_paths: RepositoryPaths, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must replace symlinks during migration
    """
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.preserve_owner")
    mocker.patch("ahriman.application.handlers.tree_migrate.walk", side_effect=[
        [
            repository_paths.archive_for(package_ahriman.base) / "file",
            repository_paths.archive_for(package_ahriman.base) / "symlink",
        ],
        [
            repository_paths.repository / "file",
            repository_paths.repository / "symlink",
        ],
    ])
    mocker.patch("pathlib.Path.exists", autospec=True, side_effect=lambda p: p.name == "file")
    unlink_mock = mocker.patch("pathlib.Path.unlink")
    symlink_mock = mocker.patch("pathlib.Path.symlink_to")

    TreeMigrate.fix_symlinks(repository_paths)
    unlink_mock.assert_called_once_with()
    symlink_mock.assert_called_once_with(
        Path("..") /
        ".." /
        ".." /
        repository_paths.archive_for(package_ahriman.base).relative_to(repository_paths.root) /
        "symlink"
    )


def test_move_tree(mocker: MockerFixture) -> None:
    """
    must move tree
    """
    rename_mock = mocker.patch("pathlib.Path.rename", autospec=True)
    root = Path("local")
    from_paths = RepositoryPaths(root, RepositoryId("arch", ""))
    to_paths = RepositoryPaths(root, RepositoryId("arch", "repo"))

    TreeMigrate.tree_move(from_paths, to_paths)
    rename_mock.assert_has_calls([
        MockCall(from_paths.packages, to_paths.packages),
        MockCall(from_paths.pacman, to_paths.pacman),
        MockCall(from_paths.repository, to_paths.repository),
    ])
