import pytest

from ahriman.core.configuration import Configuration
from ahriman.core.sign.gpg import GPG


@pytest.fixture
def gpg(configuration: Configuration) -> GPG:
    """
    fixture for empty GPG

    Args:
        configuration(Configuration): configuration fixture

    Returns:
        GPG: GPG test instance
    """
    return GPG("x86_64", configuration)


@pytest.fixture
def gpg_with_key(gpg: GPG) -> GPG:
    """
    fixture for correct GPG

    Args:
        gpg(GPG): empty GPG fixture

    Returns:
        GPG: GPG test instance
    """
    gpg.default_key = "key"
    return gpg
