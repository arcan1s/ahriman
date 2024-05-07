import datetime
import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from typing import Any, TypeVar
from unittest.mock import MagicMock

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.alpm.remote import AUR
from ahriman.core.auth import Auth
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.repository import Repository
from ahriman.core.spawn import Spawn
from ahriman.core.status import Client
from ahriman.core.status.watcher import Watcher
from ahriman.models.aur_package import AURPackage
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.package import Package
from ahriman.models.package_description import PackageDescription
from ahriman.models.package_source import PackageSource
from ahriman.models.pacman_synchronization import PacmanSynchronization
from ahriman.models.remote_source import RemoteSource
from ahriman.models.repository_id import RepositoryId
from ahriman.models.repository_paths import RepositoryPaths
from ahriman.models.result import Result
from ahriman.models.user import User
from ahriman.models.user_access import UserAccess


T = TypeVar("T")


# helpers
# https://stackoverflow.com/a/21611963
@pytest.helpers.register
def anyvar(cls: type[T], strict: bool = False) -> T:
    """
    any value helper for mocker calls check

    Args:
        cls(type[T]): type of the variable to check
        strict(bool, optional): if True then check type of supplied argument (Default value = False)

    Returns:
        T: any wrapper
    """
    class AnyVar(cls):
        """any value wrapper"""

        def __eq__(self, other: Any) -> bool:
            """
            compare object to other

            Args:
                other(Any): other object to compare

            Returns:
                bool: True in case if objects are equal
            """
            return not strict or isinstance(other, cls)

    return AnyVar()


@pytest.helpers.register
def get_package_status(package: Package) -> dict[str, Any]:
    """
    helper to extract package status from package

    Args:
        package(Package): package object

    Returns:
        dict[str, Any]: simplified package status map (with only status and view)
    """
    return {"status": BuildStatusEnum.Unknown.value, "package": package.view()}


@pytest.helpers.register
def get_package_status_extended(package: Package) -> dict[str, Any]:
    """
    helper to extract package status from package

    Args:
        package(Package): package object

    Returns:
        dict[str, Any]: full package status map (with timestamped build status and view)
    """
    return {"status": BuildStatus().view(), "package": package.view()}


@pytest.helpers.register
def import_error(package: str, components: list[str], mocker: MockerFixture) -> MagicMock:
    """
    mock import error

    Args:
        package(str): package name to import
        components(list[str]): component to import if any (e.g. from ... import ...)
        mocker(MockerFixture): mocker object

    Returns:
        MagicMock: mocked object
    """
    import builtins
    _import = builtins.__import__

    def test_import(name: str, globals: Any, locals: Any, from_list: list[str], level: Any):
        if name == package and (not components or any(component in from_list for component in components)):
            raise ImportError
        return _import(name, globals, locals, from_list, level)

    return mocker.patch.object(builtins, "__import__", test_import)


# generic fixtures
@pytest.fixture
def aur_package_ahriman() -> AURPackage:
    """
    fixture for AUR package

    Returns:
        AURPackage: AUR package test instance
    """
    return AURPackage(
        id=1197565,
        name="ahriman",
        package_base_id=165427,
        package_base="ahriman",
        version="2.6.0-1",
        description="ArcH linux ReposItory MANager",
        num_votes=0,
        popularity=0,
        first_submitted=datetime.datetime.fromtimestamp(1618008285, datetime.UTC),
        last_modified=datetime.datetime.fromtimestamp(1673826351, datetime.UTC),
        url_path="/cgit/aur.git/snapshot/ahriman.tar.gz",
        url="https://github.com/arcan1s/ahriman",
        out_of_date=None,
        maintainer="arcanis",
        submitter="arcanis",
        depends=[
            "devtools",
            "git",
            "pyalpm",
            "python-cerberus",
            "python-inflection",
            "python-passlib",
            "python-requests",
            "python-setuptools",
            "python-srcinfo",
        ],
        make_depends=[
            "python-build",
            "python-installer",
            "python-wheel",
        ],
        opt_depends=[
            "breezy",
            "darcs",
            "mercurial",
            "python-aioauth-client",
            "python-aiohttp",
            "python-aiohttp-debugtoolbar",
            "python-aiohttp-jinja2",
            "python-aiohttp-security",
            "python-aiohttp-session",
            "python-boto3",
            "python-cryptography",
            "python-requests-unixsocket",
            "python-jinja",
            "rsync",
            "subversion",
        ],
        check_depends=[
            "python-pytest",
        ],
        conflicts=[],
        provides=[],
        license=["GPL3"],
        keywords=[],
    )


@pytest.fixture
def aur_package_akonadi() -> AURPackage:
    """
    fixture for AUR package

    Returns:
        AURPackage: AUR package test instance
    """
    return AURPackage(
        id=0,
        name="akonadi",
        package_base_id=0,
        package_base="akonadi",
        version="21.12.3-2",
        description="PIM layer, which provides an asynchronous API to access all kind of PIM data",
        num_votes=0,
        popularity=0.0,
        first_submitted=datetime.datetime.fromtimestamp(0, datetime.UTC),
        last_modified=datetime.datetime.fromtimestamp(1646555990.610, datetime.UTC),
        url_path="",
        url="https://kontact.kde.org",
        out_of_date=None,
        maintainer="felixonmars",
        repository="extra",
        depends=[
            "libakonadi",
            "mariadb",
        ],
        make_depends=[
            "boost",
            "doxygen",
            "extra-cmake-modules",
            "kaccounts-integration",
            "kitemmodels",
            "postgresql",
            "qt5-tools",
        ],
        opt_depends=[
            "postgresql: PostgreSQL backend",
        ],
        conflicts=[],
        provides=[],
        license=["LGPL"],
        keywords=[],
    )


@pytest.fixture
def auth(configuration: Configuration) -> Auth:
    """
    auth provider fixture

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        Auth: auth service instance
    """
    return Auth(configuration)


@pytest.fixture
def configuration(repository_id: RepositoryId, resource_path_root: Path) -> Configuration:
    """
    configuration fixture

    Args:
        repository_id(RepositoryId): repository identifier fixture
        resource_path_root(Path): resource path root directory

    Returns:
        Configuration: configuration test instance
    """
    path = resource_path_root / "core" / "ahriman.ini"
    return Configuration.from_path(path, repository_id)


@pytest.fixture
def database(configuration: Configuration) -> SQLite:
    """
    database fixture

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        SQLite: database test instance
    """
    database = SQLite.load(configuration)
    yield database
    database.path.unlink()


@pytest.fixture
def local_client(database: SQLite, configuration: Configuration) -> Client:
    """
    local status client

    Args:
        database(SQLite): database fixture

    Returns:
        Client: local status client test instance
    """
    _, repository_id = configuration.check_loaded()
    return Client.load(repository_id, configuration, database, report=False)


@pytest.fixture
def package_ahriman(package_description_ahriman: PackageDescription, remote_source: RemoteSource) -> Package:
    """
    package fixture

    Args:
        package_description_ahriman(PackageDescription): description fixture
        remote_source(RemoteSource): remote source fixture

    Returns:
        Package: package test instance
    """
    packages = {"ahriman": package_description_ahriman}
    return Package(
        base="ahriman",
        version="2.6.0-1",
        remote=remote_source,
        packages=packages,
        packager="packager")


@pytest.fixture
def package_python_schedule(
        package_description_python_schedule: PackageDescription,
        package_description_python2_schedule: PackageDescription) -> Package:
    """
    multi package fixture

    Args:
        package_description_python_schedule(PackageDescription): description fixture
        package_description_python2_schedule(PackageDescription): description fixture

    Returns:
        Package: multi package test instance
    """
    packages = {
        "python-schedule": package_description_python_schedule,
        "python2-schedule": package_description_python2_schedule
    }
    return Package(
        base="python-schedule",
        version="1.0.0-2",
        remote=RemoteSource(
            source=PackageSource.AUR,
            git_url=AUR.remote_git_url("python-schedule", "aur"),
            web_url=AUR.remote_web_url("python-schedule"),
            path=".",
            branch="master",
        ),
        packages=packages)


@pytest.fixture
def package_description_ahriman() -> PackageDescription:
    """
    package description fixture

    Returns:
        PackageDescription: package description test instance
    """
    return PackageDescription(
        architecture="x86_64",
        archive_size=4200,
        build_date=42,
        depends=[
            "devtools",
            "git",
            "pyalpm",
            "python-cerberus",
            "python-inflection",
            "python-passlib",
            "python-requests",
            "python-setuptools",
            "python-srcinfo",
        ],
        make_depends=[
            "python-build",
            "python-installer",
            "python-wheel",
        ],
        opt_depends=[
            "breezy",
            "darcs",
            "mercurial",
            "python-aioauth-client",
            "python-aiohttp",
            "python-aiohttp-debugtoolbar",
            "python-aiohttp-jinja2",
            "python-aiohttp-security",
            "python-aiohttp-session",
            "python-boto3",
            "python-cryptography",
            "python-requests-unixsocket",
            "python-jinja",
            "rsync",
            "subversion",
        ],
        check_depends=[
            "python-pytest",
        ],
        description="ArcH linux ReposItory MANager",
        filename="ahriman-2.6.0-1-any.pkg.tar.zst",
        groups=[],
        installed_size=4200000,
        licenses=["GPL3"],
        url="https://github.com/arcan1s/ahriman")


@pytest.fixture
def package_description_python_schedule() -> PackageDescription:
    """
    package description fixture

    Returns:
        PackageDescription: package description test instance
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

    Returns:
        PackageDescription: package description test instance
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
def pacman(configuration: Configuration) -> Pacman:
    """
    fixture for pacman wrapper

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        Pacman: pacman wrapper test instance
    """
    _, repository_id = configuration.check_loaded()
    return Pacman(repository_id, configuration, refresh_database=PacmanSynchronization.Disabled)


@pytest.fixture
def passwd() -> MagicMock:
    """
    get passwd structure for the user

    Returns:
        MagicMock: passwd structure test instance
    """
    passwd = MagicMock()
    passwd.pw_dir = "home"
    passwd.pw_name = "ahriman"
    return passwd


@pytest.fixture
def remote_source() -> RemoteSource:
    """
    remote source fixture

    Returns:
        RemoteSource: remote source test instance
    """
    return RemoteSource(
        source=PackageSource.AUR,
        git_url=AUR.remote_git_url("ahriman", "aur"),
        web_url=AUR.remote_web_url("ahriman"),
        path=".",
        branch="master",
    )


@pytest.fixture
def repository(configuration: Configuration, database: SQLite, mocker: MockerFixture) -> Repository:
    """
    fixture for repository

    Args:
        configuration(Configuration): configuration fixture
        database(SQLite): database fixture
        mocker(MockerFixture): mocker object

    Returns:
        Repository: repository test instance
    """
    mocker.patch("ahriman.core.repository.Repository._set_context")
    _, repository_id = configuration.check_loaded()
    return Repository.load(repository_id, configuration, database, report=False)


@pytest.fixture
def repository_id() -> RepositoryId:
    """
    fixture for repository identifier

    Returns:
        RepositoryId: repository identifier test instance
    """
    return RepositoryId("x86_64", "aur-clone")


@pytest.fixture
def repository_paths(configuration: Configuration) -> RepositoryPaths:
    """
    repository paths fixture

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        RepositoryPaths: repository paths test instance
    """
    return configuration.repository_paths


@pytest.fixture
def result(package_ahriman: Package) -> Result:
    """
    result fixture

    Args:
        package_ahriman(Package): package fixture

    Returns:
        Result: result test instance
    """
    result = Result()
    result.add_updated(package_ahriman)
    return result


@pytest.fixture
def spawner(configuration: Configuration) -> Spawn:
    """
    spawner fixture

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        Spawn: spawner fixture
    """
    return Spawn(MagicMock(), [
        "--configuration", str(configuration.path),
    ])


@pytest.fixture
def user() -> User:
    """
    fixture for user descriptor

    Returns:
        User: user descriptor instance
    """
    return User(username="user", password="pa55w0rd", access=UserAccess.Reporter, packager_id="packager", key="key")


@pytest.fixture
def watcher(local_client: Client) -> Watcher:
    """
    package status watcher fixture

    Args:
        local_client(Client): local status client fixture

    Returns:
        Watcher: package status watcher test instance
    """
    return Watcher(local_client)
