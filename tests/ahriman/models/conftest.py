import pytest

from pathlib import Path

from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.package import Package
from ahriman.models.package_desciption import PackageDescription
from ahriman.models.repository_paths import RepositoryPaths


@pytest.fixture
def build_status_failed() -> BuildStatus:
    return BuildStatus(BuildStatusEnum.Failed, 42)


@pytest.fixture
def package_ahriman(package_description_ahriman: PackageDescription) -> Package:
    packages = {"ahriman": package_description_ahriman}
    return Package(
        base="ahriman",
        version="0.12.1-1",
        aur_url="https://aur.archlinux.org",
        packages=packages)


@pytest.fixture
def package_python_schedule(
        package_description_python_schedule: PackageDescription,
        package_description_python2_schedule: PackageDescription) -> Package:
    packages = {
        "python-schedule": package_description_python_schedule,
        "python2-schedule": package_description_python2_schedule
    }
    return Package(
        base="python-schedule",
        version="1.0.0-2",
        aur_url="https://aur.archlinux.org",
        packages=packages)


@pytest.fixture
def package_tpacpi_bat_git() -> Package:
    return Package(
        base="tpacpi-bat-git",
        version="3.1.r12.g4959b52-1",
        aur_url="https://aur.archlinux.org",
        packages={"tpacpi-bat-git": PackageDescription()})


@pytest.fixture
def package_description_ahriman() -> PackageDescription:
    return PackageDescription(
        archive_size=4200,
        build_date=42,
        filename="ahriman-0.12.1-1-any.pkg.tar.zst",
        installed_size=4200000)


@pytest.fixture
def package_description_python_schedule() -> PackageDescription:
    return PackageDescription(
        archive_size=4201,
        build_date=421,
        filename="python-schedule-1.0.0-2-any.pkg.tar.zst",
        installed_size=4200001)


@pytest.fixture
def package_description_python2_schedule() -> PackageDescription:
    return PackageDescription(
        archive_size=4202,
        build_date=422,
        filename="python2-schedule-1.0.0-2-any.pkg.tar.zst",
        installed_size=4200002)


@pytest.fixture
def repository_paths() -> RepositoryPaths:
    return RepositoryPaths(
        architecture="x86_64",
        root=Path("/var/lib/ahriman"))
