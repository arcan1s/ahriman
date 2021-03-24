import pytest

from pathlib import Path

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.alpm.repo import Repo
from ahriman.core.configuration import Configuration
from ahriman.models.repository_paths import RepositoryPaths


@pytest.fixture
def configuration(resource_path_root: Path) -> Configuration:
    path = resource_path_root / "core" / "ahriman.ini"
    return Configuration.from_path(path=path, logfile=False)


@pytest.fixture
def pacman(configuration: Configuration) -> Pacman:
    return Pacman(configuration)


@pytest.fixture
def repo(configuration: Configuration) -> Repo:
    return Repo(
        configuration.get("repository", "name"),
        RepositoryPaths(Path(configuration.get("repository", "root")), "x86_64"),
        [])
