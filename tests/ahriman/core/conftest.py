import pytest

from pathlib import Path

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.alpm.repo import Repo
from ahriman.core.build_tools.task import Task
from ahriman.core.configuration import Configuration
from ahriman.models.package import Package
from ahriman.models.repository_paths import RepositoryPaths


@pytest.fixture
def configuration(resource_path_root: Path) -> Configuration:
    path = resource_path_root / "core" / "ahriman.ini"
    return Configuration.from_path(path=path, logfile=False)


@pytest.fixture
def pacman(configuration: Configuration) -> Pacman:
    return Pacman(configuration)


@pytest.fixture
def repo(configuration: Configuration, repository_paths: RepositoryPaths) -> Repo:
    return Repo(configuration.get("repository", "name"), repository_paths, [])


@pytest.fixture
def task_ahriman(package_ahriman: Package, configuration: Configuration, repository_paths: RepositoryPaths) -> Task:
    return Task(package_ahriman, "x86_64", configuration, repository_paths)
