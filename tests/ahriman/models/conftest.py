import pytest
import time

from unittest.mock import MagicMock, PropertyMock

from ahriman import version
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.counters import Counters
from ahriman.models.internal_status import InternalStatus
from ahriman.models.package import Package
from ahriman.models.package_description import PackageDescription
from ahriman.models.user_identity import UserIdentity


@pytest.fixture
def build_status_failed() -> BuildStatus:
    """
    build result fixture with failed status
    :return: failed build status test instance
    """
    return BuildStatus(BuildStatusEnum.Failed, 42)


@pytest.fixture
def counters() -> Counters:
    """
    counters fixture
    :return: counters test instance
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
    :param counters: counters fixture
    :return: internal status test instance
    """
    return InternalStatus(architecture="x86_64",
                          packages=counters,
                          version=version.__version__,
                          repository="aur-clone")


@pytest.fixture
def package_tpacpi_bat_git() -> Package:
    """
    git package fixture
    :return: git package test instance
    """
    return Package(
        base="tpacpi-bat-git",
        version="3.1.r12.g4959b52-1",
        aur_url="https://aur.archlinux.org",
        packages={"tpacpi-bat-git": PackageDescription()})


@pytest.fixture
def pyalpm_handle(pyalpm_package_ahriman: MagicMock) -> MagicMock:
    """
    mock object for pyalpm
    :param pyalpm_package_ahriman: mock object for pyalpm package
    :return: pyalpm mock
    """
    mock = MagicMock()
    mock.handle.load_pkg.return_value = pyalpm_package_ahriman
    return mock


@pytest.fixture
def pyalpm_package_ahriman(package_ahriman: Package) -> MagicMock:
    """
    mock object for pyalpm package
    :param package_ahriman: package fixture
    :return: pyalpm package mock
    """
    mock = MagicMock()
    type(mock).base = PropertyMock(return_value=package_ahriman.base)
    type(mock).name = PropertyMock(return_value=package_ahriman.base)
    type(mock).version = PropertyMock(return_value=package_ahriman.version)
    return mock


@pytest.fixture
def pyalpm_package_description_ahriman(package_description_ahriman: PackageDescription) -> MagicMock:
    """
    mock object for pyalpm package description
    :param package_description_ahriman: package description fixture
    :return: pyalpm package description mock
    """
    mock = MagicMock()
    type(mock).arch = PropertyMock(return_value=package_description_ahriman.architecture)
    type(mock).builddate = PropertyMock(return_value=package_description_ahriman.build_date)
    type(mock).depends = PropertyMock(return_value=package_description_ahriman.depends)
    type(mock).desc = PropertyMock(return_value=package_description_ahriman.description)
    type(mock).groups = PropertyMock(return_value=package_description_ahriman.groups)
    type(mock).isize = PropertyMock(return_value=package_description_ahriman.installed_size)
    type(mock).licenses = PropertyMock(return_value=package_description_ahriman.licenses)
    type(mock).size = PropertyMock(return_value=package_description_ahriman.archive_size)
    type(mock).provides = PropertyMock(return_value=package_description_ahriman.provides)
    type(mock).url = PropertyMock(return_value=package_description_ahriman.url)
    return mock


@pytest.fixture
def user_identity() -> UserIdentity:
    """
    identity fixture
    :return: user identity test instance
    """
    return UserIdentity("username", int(time.time()) + 30)
