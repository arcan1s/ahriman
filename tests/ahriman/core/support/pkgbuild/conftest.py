import pytest

from ahriman.core.configuration import Configuration
from ahriman.core.sign.gpg import GPG
from ahriman.core.support.pkgbuild.keyring_generator import KeyringGenerator
from ahriman.core.support.pkgbuild.pkgbuild_generator import PkgbuildGenerator


@pytest.fixture
def keyring_generator(gpg: GPG, configuration: Configuration) -> KeyringGenerator:
    """
    fixture for keyring pkgbuild generator

    Args:
        gpg(GPG): empty GPG fixture
        configuration(Configuration): configuration fixture

    Returns:
        KeyringGenerator: keyring generator test instance
    """
    return KeyringGenerator(gpg, configuration, "keyring")


@pytest.fixture
def pkgbuild_generator() -> PkgbuildGenerator:
    """
    fixture for dummy pkgbuild generator

    Returns:
        PkgbuildGenerator: pkgbuild generator test instance
    """
    return PkgbuildGenerator()
