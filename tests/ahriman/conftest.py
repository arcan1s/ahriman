import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from typing import Any, Type, TypeVar

from ahriman.core.configuration import Configuration
from ahriman.core.status.watcher import Watcher
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
def configuration(resource_path_root: Path) -> Configuration:
    path = resource_path_root / "core" / "ahriman.ini"
    return Configuration.from_path(path=path, logfile=False)


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
def package_description_ahriman() -> PackageDescription:
    return PackageDescription(
        architecture="x86_64",
        archive_size=4200,
        build_date=42,
        description="ArcHlinux ReposItory MANager",
        filename="ahriman-0.12.1-1-any.pkg.tar.zst",
        groups=[],
        installed_size=4200000,
        licenses=["GPL3"],
        url="https://github.com/arcan1s/ahriman")


@pytest.fixture
def package_description_python_schedule() -> PackageDescription:
    return PackageDescription(
        architecture="x86_64",
        archive_size=4201,
        build_date=421,
        description="Python job scheduling for humans.",
        filename="python-schedule-1.0.0-2-any.pkg.tar.zst",
        groups=[],
        installed_size=4200001,
        licenses=["MIT"],
        url="https://github.com/dbader/schedule")


@pytest.fixture
def package_description_python2_schedule() -> PackageDescription:
    return PackageDescription(
        architecture="x86_64",
        archive_size=4202,
        build_date=422,
        description="Python job scheduling for humans.",
        filename="python2-schedule-1.0.0-2-any.pkg.tar.zst",
        groups=[],
        installed_size=4200002,
        licenses=["MIT"],
        url="https://github.com/dbader/schedule")


@pytest.fixture
def repository_paths(configuration: Configuration) -> RepositoryPaths:
    return RepositoryPaths(
        architecture="x86_64",
        root=configuration.getpath("repository", "root"))


@pytest.fixture
def watcher(configuration: Configuration, mocker: MockerFixture) -> Watcher:
    mocker.patch("pathlib.Path.mkdir")
    return Watcher("x86_64", configuration)
