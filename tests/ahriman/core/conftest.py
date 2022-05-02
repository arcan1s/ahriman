import pytest

from ahriman.core.alpm.repo import Repo
from ahriman.core.build_tools.task import Task
from ahriman.core.configuration import Configuration
from ahriman.core.tree import Leaf
from ahriman.models.package import Package
from ahriman.models.repository_paths import RepositoryPaths


@pytest.fixture
def leaf_ahriman(package_ahriman: Package) -> Leaf:
    """
    fixture for tree leaf with package

    Args:
        package_ahriman(Package): package fixture

    Returns:
        Leaf: tree leaf test instance
    """
    return Leaf(package_ahriman, set())


@pytest.fixture
def leaf_python_schedule(package_python_schedule: Package) -> Leaf:
    """
    fixture for tree leaf with package

    Args:
        package_python_schedule(Package): package fixture

    Returns:
        Leaf: tree leaf test instance
    """
    return Leaf(package_python_schedule, set())


@pytest.fixture
def repo(configuration: Configuration, repository_paths: RepositoryPaths) -> Repo:
    """
    fixture for repository wrapper

    Args:
        configuration(Configuration): configuration fixture
        repository_paths(RepositoryPaths): repository paths fixture

    Returns:
        Repo: repository wrapper test instance
    """
    return Repo(configuration.get("repository", "name"), repository_paths, [])


@pytest.fixture
def task_ahriman(package_ahriman: Package, configuration: Configuration, repository_paths: RepositoryPaths) -> Task:
    """
    fixture for built task

    Args:
        package_ahriman(Package): package fixture
        configuration(Configuration): configuration fixture
        repository_paths(RepositoryPaths): repository paths fixture

    Returns:
        Task: built task test instance
    """
    return Task(package_ahriman, configuration, repository_paths)
