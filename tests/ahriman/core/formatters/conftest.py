import pytest

from ahriman.core.formatters.aur_printer import AurPrinter
from ahriman.core.formatters.configuration_printer import ConfigurationPrinter
from ahriman.core.formatters.package_printer import PackagePrinter
from ahriman.core.formatters.status_printer import StatusPrinter
from ahriman.core.formatters.string_printer import StringPrinter
from ahriman.core.formatters.update_printer import UpdatePrinter
from ahriman.core.formatters.user_printer import UserPrinter
from ahriman.models.aur_package import AURPackage
from ahriman.models.build_status import BuildStatus
from ahriman.models.package import Package
from ahriman.models.user import User


@pytest.fixture
def aur_package_ahriman_printer(aur_package_ahriman: AURPackage) -> AurPrinter:
    """
    fixture for AUR package printer

    Args:
      aur_package_ahriman(AURPackage): AUR package fixture

    Returns:
      AurPrinter: AUR package printer test instance
    """
    return AurPrinter(aur_package_ahriman)


@pytest.fixture
def configuration_printer() -> ConfigurationPrinter:
    """
    fixture for configuration printer

    Returns:
      ConfigurationPrinter: configuration printer test instance
    """
    return ConfigurationPrinter("section", {"key_one": "value_one", "key_two": "value_two"})


@pytest.fixture
def package_ahriman_printer(package_ahriman: Package) -> PackagePrinter:
    """
    fixture for package printer

    Args:
      package_ahriman(Package): package fixture

    Returns:
      PackagePrinter: package printer test instance
    """
    return PackagePrinter(package_ahriman, BuildStatus())


@pytest.fixture
def status_printer() -> StatusPrinter:
    """
    fixture for build status printer

    Returns:
      StatusPrinter: build status printer test instance
    """
    return StatusPrinter(BuildStatus())


@pytest.fixture
def string_printer() -> StringPrinter:
    """
    fixture for any string printer

    Returns:
      StringPrinter: any string printer test instance
    """
    return StringPrinter("hello, world")


@pytest.fixture
def update_printer(package_ahriman: Package) -> UpdatePrinter:
    """
    fixture for build status printer

    Args:
      package_ahriman(Package): package fixture

    Returns:
      UpdatePrinter: build status printer test instance
    """
    return UpdatePrinter(package_ahriman, None)


@pytest.fixture
def user_printer(user: User) -> UserPrinter:
    """
    fixture for user printer

    Args:
      user(User): user fixture

    Returns:
      UserPrinter: user printer test instance
    """
    return UserPrinter(user)
