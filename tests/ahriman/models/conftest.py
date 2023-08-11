import datetime
import pytest

from unittest.mock import MagicMock, PropertyMock

from ahriman import __version__
from ahriman.core.alpm.remote import AUR
from ahriman.models.aur_package import AURPackage
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.counters import Counters
from ahriman.models.internal_status import InternalStatus
from ahriman.models.package import Package
from ahriman.models.package_description import PackageDescription
from ahriman.models.package_source import PackageSource
from ahriman.models.remote_source import RemoteSource


@pytest.fixture
def build_status_failed() -> BuildStatus:
    """
    build result fixture with failed status

    Returns:
        BuildStatus: failed build status test instance
    """
    return BuildStatus(BuildStatusEnum.Failed, 42)


@pytest.fixture
def counters() -> Counters:
    """
    counters fixture

    Returns:
        Counters: counters test instance
    """
    return Counters(total=10,
                    unknown=1,
                    pending=2,
                    building=3,
                    failed=4,
                    success=0)


@pytest.fixture
def internal_status(counters: Counters) -> InternalStatus:
    """
    internal status fixture

    Args:
        counters(Counters): counters fixture

    Returns:
        InternalStatus: internal status test instance
    """
    return InternalStatus(status=BuildStatus(),
                          architecture="x86_64",
                          packages=counters,
                          version=__version__,
                          repository="aur-clone")


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
def pyalpm_handle(pyalpm_package_ahriman: MagicMock) -> MagicMock:
    """
    mock object for pyalpm

    Args:
        pyalpm_package_ahriman(MagicMock): mock object for pyalpm package

    Returns:
        MagicMock: pyalpm mock
    """
    mock = MagicMock()
    mock.handle.load_pkg.return_value = pyalpm_package_ahriman
    return mock


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

    return mock


@pytest.fixture
def pyalpm_package_description_ahriman(package_description_ahriman: PackageDescription) -> MagicMock:
    """
    mock object for pyalpm package description

    Args:
        package_description_ahriman(PackageDescription): package description fixture

    Returns:
        MagicMock: pyalpm package description mock
    """
    mock = MagicMock()
    type(mock).arch = PropertyMock(return_value=package_description_ahriman.architecture)
    type(mock).builddate = PropertyMock(return_value=package_description_ahriman.build_date)
    type(mock).depends = PropertyMock(return_value=package_description_ahriman.depends)
    type(mock).makedepends = PropertyMock(return_value=package_description_ahriman.make_depends)
    type(mock).optdepends = PropertyMock(return_value=package_description_ahriman.opt_depends)
    type(mock).checkdepends = PropertyMock(return_value=package_description_ahriman.check_depends)
    type(mock).desc = PropertyMock(return_value=package_description_ahriman.description)
    type(mock).groups = PropertyMock(return_value=package_description_ahriman.groups)
    type(mock).isize = PropertyMock(return_value=package_description_ahriman.installed_size)
    type(mock).licenses = PropertyMock(return_value=package_description_ahriman.licenses)
    type(mock).size = PropertyMock(return_value=package_description_ahriman.archive_size)
    type(mock).provides = PropertyMock(return_value=package_description_ahriman.provides)
    type(mock).url = PropertyMock(return_value=package_description_ahriman.url)
    return mock
