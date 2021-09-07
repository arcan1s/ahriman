import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from typing import Any, Type, TypeVar
from unittest.mock import MagicMock

from ahriman.core.auth.auth import Auth
from ahriman.core.configuration import Configuration
from ahriman.core.spawn import Spawn
from ahriman.core.status.watcher import Watcher
from ahriman.models.package import Package
from ahriman.models.package_description import PackageDescription
from ahriman.models.repository_paths import RepositoryPaths
from ahriman.models.user import User
from ahriman.models.user_access import UserAccess


T = TypeVar("T")


# helpers
# https://stackoverflow.com/a/21611963
@pytest.helpers.register
def anyvar(cls: Type[T], strict: bool = False) -> T:
    """
    any value helper for mocker calls check
    :param cls: type class
    :param strict: if True then check type of supplied argument
    :return: any wrapper
    """
    class AnyVar(cls):
        """
        any value wrapper
        """

        def __eq__(self, other: Any) -> bool:
            """
            compare object to other
            :param other: other object to compare
            :return: True in case if objects are equal
            """
            return not strict or isinstance(other, cls)

    return AnyVar()


# generic fixtures
@pytest.fixture
def auth(configuration: Configuration) -> Auth:
    """
    auth provider fixture
    :param configuration: configuration fixture
    :return: auth service instance
    """
    return Auth(configuration)


@pytest.fixture
def configuration(resource_path_root: Path) -> Configuration:
    """
    configuration fixture
    :param resource_path_root: resource path root directory
    :return: configuration test instance
    """
    path = resource_path_root / "core" / "ahriman.ini"
    return Configuration.from_path(path=path, architecture="x86_64", logfile=False)


@pytest.fixture
def package_ahriman(package_description_ahriman: PackageDescription) -> Package:
    """
    package fixture
    :param package_description_ahriman: description fixture
    :return: package test instance
    """
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
    """
    multi package fixture
    :param package_description_python_schedule: description fixture
    :param package_description_python2_schedule: description fixture
    :return: multi package test instance
    """
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
    """
    package description fixture
    :return: package description test instance
    """
    return PackageDescription(
        architecture="x86_64",
        archive_size=4200,
        build_date=42,
        depends=["devtools", "git", "pyalpm", "python-aur", "python-srcinfo"],
        description="ArcHlinux ReposItory MANager",
        filename="ahriman-0.12.1-1-any.pkg.tar.zst",
        groups=[],
        installed_size=4200000,
        licenses=["GPL3"],
        url="https://github.com/arcan1s/ahriman")


@pytest.fixture
def package_description_python_schedule() -> PackageDescription:
    """
    package description fixture
    :return: package description test instance
    """
    return PackageDescription(
        architecture="x86_64",
        archive_size=4201,
        build_date=421,
        depends=["python"],
        description="Python job scheduling for humans.",
        filename="python-schedule-1.0.0-2-any.pkg.tar.zst",
        groups=[],
        installed_size=4200001,
        licenses=["MIT"],
        url="https://github.com/dbader/schedule")


@pytest.fixture
def package_description_python2_schedule() -> PackageDescription:
    """
    package description fixture
    :return: package description test instance
    """
    return PackageDescription(
        architecture="x86_64",
        archive_size=4202,
        build_date=422,
        depends=["python2"],
        description="Python job scheduling for humans.",
        filename="python2-schedule-1.0.0-2-any.pkg.tar.zst",
        groups=[],
        installed_size=4200002,
        licenses=["MIT"],
        url="https://github.com/dbader/schedule")


@pytest.fixture
def repository_paths(configuration: Configuration) -> RepositoryPaths:
    """
    repository paths fixture
    :param configuration: configuration fixture
    :return: repository paths test instance
    """
    return RepositoryPaths(
        architecture="x86_64",
        root=configuration.getpath("repository", "root"))


@pytest.fixture
def spawner(configuration: Configuration) -> Spawn:
    """
    spawner fixture
    :param configuration: configuration fixture
    :return: spawner fixture
    """
    return Spawn(MagicMock(), "x86_64", configuration)


@pytest.fixture
def user() -> User:
    """
    fixture for user descriptor
    :return: user descriptor instance
    """
    return User("user", "pa55w0rd", UserAccess.Status)


@pytest.fixture
def watcher(configuration: Configuration, mocker: MockerFixture) -> Watcher:
    """
    package status watcher fixture
    :param configuration: configuration fixture
    :param mocker: mocker object
    :return: package status watcher test instance
    """
    mocker.patch("pathlib.Path.mkdir")
    return Watcher("x86_64", configuration)
