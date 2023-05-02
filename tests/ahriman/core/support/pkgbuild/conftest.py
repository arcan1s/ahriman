import pytest

from ahriman.core.support.pkgbuild.pkgbuild_generator import PkgbuildGenerator


@pytest.fixture
def pkgbuild_generator() -> PkgbuildGenerator:
    """
    fixture for dummy pkgbuild generator

    Returns:
        PkgbuildGenerator: pkgbuild generator test instance
    """
    return PkgbuildGenerator()
