from dataclasses import asdict

from ahriman.models.package import Package
from ahriman.models.repository_stats import RepositoryStats


def test_repository_stats_from_json_view(package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must construct same object from json
    """
    stats = RepositoryStats.from_packages([package_ahriman, package_python_schedule])
    assert RepositoryStats.from_json(asdict(stats)) == stats


def test_from_packages(package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must generate stats from packages list
    """
    assert RepositoryStats.from_packages([package_ahriman, package_python_schedule]) == RepositoryStats(
        bases=2,
        packages=3,
        archive_size=12603,
        installed_size=12600003,
    )
