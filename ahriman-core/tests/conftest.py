import datetime
import pytest

from unittest.mock import MagicMock, PropertyMock

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.alpm.remote import AUR
from ahriman.core.configuration import Configuration
from ahriman.models.aur_package import AURPackage
from ahriman.models.package import Package
from ahriman.models.package_description import PackageDescription
from ahriman.models.package_source import PackageSource
from ahriman.models.pacman_synchronization import PacmanSynchronization
from ahriman.models.remote_source import RemoteSource
from ahriman.models.scan_paths import ScanPaths


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
        groups=[],
    )


@pytest.fixture
def package_tpacpi_bat_git() -> Package:
    """
    git package fixture

    Returns:
        Package: git package test instance
    """
    return Package(
        base="tpacpi-bat-git",
        version="3.1.r12.g4959b52-1",
        remote=RemoteSource(
            source=PackageSource.AUR,
            git_url=AUR.remote_git_url("tpacpi-bat-git", "aur"),
            web_url=AUR.remote_web_url("tpacpi-bat-git"),
            path=".",
            branch="master",
        ),
        packages={"tpacpi-bat-git": PackageDescription()})


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
def pyalpm_package_ahriman(aur_package_ahriman: AURPackage) -> MagicMock:
    """
    mock object for pyalpm package

    Args:
        aur_package_ahriman(AURPackage): package fixture

    Returns:
        MagicMock: pyalpm package mock
    """
    mock = MagicMock()
    db = type(mock).db = MagicMock()

    type(mock).base = PropertyMock(return_value=aur_package_ahriman.package_base)
    type(mock).builddate = PropertyMock(
        return_value=aur_package_ahriman.last_modified.replace(tzinfo=datetime.timezone.utc).timestamp())
    type(mock).conflicts = PropertyMock(return_value=aur_package_ahriman.conflicts)
    type(db).name = PropertyMock(return_value="aur")
    type(mock).depends = PropertyMock(return_value=aur_package_ahriman.depends)
    type(mock).desc = PropertyMock(return_value=aur_package_ahriman.description)
    type(mock).licenses = PropertyMock(return_value=aur_package_ahriman.license)
    type(mock).makedepends = PropertyMock(return_value=aur_package_ahriman.make_depends)
    type(mock).name = PropertyMock(return_value=aur_package_ahriman.name)
    type(mock).optdepends = PropertyMock(return_value=aur_package_ahriman.opt_depends)
    type(mock).checkdepends = PropertyMock(return_value=aur_package_ahriman.check_depends)
    type(mock).packager = PropertyMock(return_value="packager")
    type(mock).provides = PropertyMock(return_value=aur_package_ahriman.provides)
    type(mock).version = PropertyMock(return_value=aur_package_ahriman.version)
    type(mock).url = PropertyMock(return_value=aur_package_ahriman.url)
    type(mock).groups = PropertyMock(return_value=aur_package_ahriman.groups)

    return mock


@pytest.fixture
def scan_paths(configuration: Configuration) -> ScanPaths:
    """
    scan paths fixture

    Args:
        configuration(Configuration): configuration test instance

    Returns:
        ScanPaths: scan paths test instance
    """
    return ScanPaths(configuration.getlist("build", "scan_paths", fallback=[]))
