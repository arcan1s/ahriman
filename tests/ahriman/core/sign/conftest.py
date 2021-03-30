import pytest

from ahriman.core.configuration import Configuration
from ahriman.core.sign.gpg import GPG


@pytest.fixture
def gpg(configuration: Configuration) -> GPG:
    return GPG("x86_64", configuration)


@pytest.fixture
def gpg_with_key(gpg: GPG) -> GPG:
    gpg.default_key = "key"
    return gpg
