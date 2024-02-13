import argparse

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import MagicMock

from ahriman.application.handlers import Backup
from ahriman.core.configuration import Configuration
from ahriman.models.repository_paths import RepositoryPaths


def _default_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    default arguments for these test cases

    Args:
        args(argparse.Namespace): command line arguments fixture

    Returns:
        argparse.Namespace: generated arguments for these test cases
    """
    args.path = Path("result.tar.gz")
    return args


def test_run(args: argparse.Namespace, configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must run command
    """
    args = _default_args(args)
    mocker.patch("ahriman.application.handlers.Backup.get_paths", return_value=[Path("path")])
    tarfile = MagicMock()
    add_mock = tarfile.__enter__.return_value = MagicMock()
    mocker.patch("ahriman.application.handlers.backup.tarfile.open", return_value=tarfile)

    _, repository_id = configuration.check_loaded()
    Backup.run(args, repository_id, configuration, report=False)
    add_mock.add.assert_called_once_with(Path("path"))


def test_get_paths(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must get paths to be archived
    """
    # gnupg export mock
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch.object(RepositoryPaths, "root_owner", (42, 42))
    getpwuid_mock = mocker.patch("ahriman.application.handlers.backup.getpwuid", return_value=MagicMock())
    # well database does not exist so we override it
    database_mock = mocker.patch("ahriman.core.database.SQLite.database_path", return_value=configuration.path)

    paths = Backup.get_paths(configuration)
    getpwuid_mock.assert_called_once_with(42)
    database_mock.assert_called_once_with(configuration)
    assert configuration.path in paths
    assert all(path.exists() for path in paths if path.name not in (".gnupg", "cache"))


def test_disallow_multi_architecture_run() -> None:
    """
    must not allow multi architecture run
    """
    assert not Backup.ALLOW_MULTI_ARCHITECTURE_RUN
