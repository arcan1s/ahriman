import pytest

from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.package import Package
from ahriman.models.package_desciption import PackageDescription


@pytest.fixture
def build_status_failed() -> BuildStatus:
    return BuildStatus(BuildStatusEnum.Failed, 42)


@pytest.fixture
def package_tpacpi_bat_git() -> Package:
    return Package(
        base="tpacpi-bat-git",
        version="3.1.r12.g4959b52-1",
        aur_url="https://aur.archlinux.org",
        packages={"tpacpi-bat-git": PackageDescription()})
