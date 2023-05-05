import pytest

from ahriman.core.sign.gpg import GPG


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
