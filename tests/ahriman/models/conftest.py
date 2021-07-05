import pytest

from unittest.mock import MagicMock, PropertyMock

from ahriman import version
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.counters import Counters
from ahriman.models.internal_status import InternalStatus
from ahriman.models.package import Package
from ahriman.models.package_description import PackageDescription


@pytest.fixture
def build_status_failed() -> BuildStatus:
    return BuildStatus(BuildStatusEnum.Failed, 42)


@pytest.fixture
def counters() -> Counters:
    return Counters(total=10,
                    unknown=1,
                    pending=2,
                    building=3,
                    failed=4,
                    success=0)


@pytest.fixture
def internal_status(counters: Counters) -> InternalStatus:
    return InternalStatus(architecture="x86_64",
                          packages=counters,
                          version=version.__version__,
                          repository="aur-clone")


@pytest.fixture
def package_tpacpi_bat_git() -> Package:
    return Package(
        base="tpacpi-bat-git",
        version="3.1.r12.g4959b52-1",
        aur_url="https://aur.archlinux.org",
        packages={"tpacpi-bat-git": PackageDescription()})


@pytest.fixture
def pyalpm_handle(pyalpm_package_ahriman: MagicMock) -> MagicMock:
    mock = MagicMock()
    mock.handle.load_pkg.return_value = pyalpm_package_ahriman
    return mock


@pytest.fixture
def pyalpm_package_ahriman(package_ahriman: Package) -> MagicMock:
    mock = MagicMock()
    type(mock).base = PropertyMock(return_value=package_ahriman.base)
    type(mock).name = PropertyMock(return_value=package_ahriman.base)
    type(mock).version = PropertyMock(return_value=package_ahriman.version)
    return mock


@pytest.fixture
def pyalpm_package_description_ahriman(package_description_ahriman: PackageDescription) -> MagicMock:
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
