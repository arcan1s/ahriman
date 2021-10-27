import aur
import pytest

from ahriman.application.formatters.aur_printer import AurPrinter
from ahriman.application.formatters.configuration_printer import ConfigurationPrinter
from ahriman.application.formatters.package_printer import PackagePrinter
from ahriman.application.formatters.status_printer import StatusPrinter
from ahriman.application.formatters.update_printer import UpdatePrinter
from ahriman.models.build_status import BuildStatus
from ahriman.models.package import Package


@pytest.fixture
def aur_package_ahriman_printer(aur_package_ahriman: aur.Package) -> AurPrinter:
    """
    fixture for AUR package printer
    :param aur_package_ahriman: AUR package fixture
    :return: AUR package printer test instance
    """
    return AurPrinter(aur_package_ahriman)


@pytest.fixture
def configuration_printer() -> ConfigurationPrinter:
    """
    fixture for configuration printer
    :return: configuration printer test instance
    """
    return ConfigurationPrinter("section", {"key_one": "value_one", "key_two": "value_two"})


@pytest.fixture
def package_ahriman_printer(package_ahriman: Package) -> PackagePrinter:
    """
    fixture for package printer
    :param package_ahriman: package fixture
    :return: package printer test instance
    """
    return PackagePrinter(package_ahriman, BuildStatus())


@pytest.fixture
def status_printer() -> StatusPrinter:
    """
    fixture for build status printer
    :return: build status printer test instance
    """
    return StatusPrinter(BuildStatus())


@pytest.fixture
def update_printer(package_ahriman: Package) -> UpdatePrinter:
    """
    fixture for build status printer
    :return: build status printer test instance
    """
    return UpdatePrinter(package_ahriman, None)
