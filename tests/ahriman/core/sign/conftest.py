import pytest

from ahriman.core.configuration import Configuration
from ahriman.core.sign.gpg import GPG


@pytest.fixture
def gpg(configuration: Configuration) -> GPG:
    """
    fixture for empty GPG
    :param configuration: configuration fixture
    :return: GPG test instance
    """
    return GPG("x86_64", configuration)


@pytest.fixture
def gpg_with_key(gpg: GPG) -> GPG:
    """
    fixture for correct GPG
    :param gpg: empty GPG fixture
    :return: GPG test instance
    """
    gpg.default_key = "key"
    return gpg
