import pytest

from pytest_mock import MockerFixture
from typing import Any

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.build_tools.package_archive import PackageArchive
from ahriman.core.build_tools.sources import Sources
from ahriman.models.package import Package
from ahriman.models.repository_paths import RepositoryPaths
from ahriman.models.scan_paths import ScanPaths


@pytest.fixture
def package_archive_ahriman(package_ahriman: Package, repository_paths: RepositoryPaths, pacman: Pacman,
                            scan_paths: ScanPaths, passwd: Any, mocker: MockerFixture) -> PackageArchive:
    """
    package archive fixture

    Args:
        package_ahriman(Package): package test instance
        repository_paths(RepositoryPaths): repository paths test instance
        pacman(Pacman): pacman test instance
        scan_paths(ScanPaths): scan paths test instance
        passwd(Any): passwd structure test instance
        mocker(MockerFixture): mocker object

    Returns:
        PackageArchive: package archive test instance
    """
    mocker.patch("ahriman.models.repository_paths.getpwuid", return_value=passwd)
    return PackageArchive(repository_paths.build_directory, package_ahriman, pacman, scan_paths)


@pytest.fixture
def sources() -> Sources:
    """
    sources fixture

    Returns:
        Sources: sources instance
    """
    return Sources()
