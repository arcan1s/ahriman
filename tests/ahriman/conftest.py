import pytest

from pathlib import Path
from typing import Any, Type, TypeVar

from ahriman.models.package import Package
from ahriman.models.package_desciption import PackageDescription
from ahriman.models.repository_paths import RepositoryPaths

T = TypeVar("T")


# helpers
# https://stackoverflow.com/a/21611963
@pytest.helpers.register
def anyvar(cls: Type[T], strict: bool = False) -> T:
    class AnyVar(cls):
        def __eq__(self, other: Any) -> bool:
            return not strict or isinstance(other, cls)
    return AnyVar()


# generic fixtures
@pytest.fixture
def package_ahriman(package_description_ahriman: PackageDescription) -> Package:
    packages = {"ahriman": package_description_ahriman}
    return Package(
        base="ahriman",
        version="0.12.1-1",
        aur_url="https://aur.archlinux.org",
        packages=packages)


@pytest.fixture
def package_description_ahriman() -> PackageDescription:
    return PackageDescription(
        archive_size=4200,
        build_date=42,
        filename="ahriman-0.12.1-1-any.pkg.tar.zst",
        installed_size=4200000)


@pytest.fixture
def repository_paths() -> RepositoryPaths:
    return RepositoryPaths(
        architecture="x86_64",
        root=Path("/var/lib/ahriman"))
