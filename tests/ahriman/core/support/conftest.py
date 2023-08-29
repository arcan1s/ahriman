import pytest

from ahriman.core.configuration import Configuration
from ahriman.core.support.package_creator import PackageCreator
from ahriman.core.support.pkgbuild.mirrorlist_generator import MirrorlistGenerator


@pytest.fixture
def mirrorlist_generator(configuration: Configuration) -> MirrorlistGenerator:
    """
    fixture for mirrorlist pkgbuild generator

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        MirrorlistGenerator: mirrorlist pkgbuild generator test instance
    """
    _, repository_id = configuration.check_loaded()
    return MirrorlistGenerator(repository_id, configuration, "mirrorlist")


@pytest.fixture
def package_creator(configuration: Configuration, mirrorlist_generator: MirrorlistGenerator) -> PackageCreator:
    """
    package creator fixture

    Args:
        configuration(Configuration): configuration fixture
        mirrorlist_generator(MirrorlistGenerator):

    Returns:
        PackageCreator: package creator test instance
    """
    return PackageCreator(configuration, mirrorlist_generator)
