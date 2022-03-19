import pytest

from ahriman.core.formatters.build_printer import BuildPrinter
from ahriman.models.package import Package


def test_properties(package_ahriman: Package) -> None:
    """
    must return empty properties list
    """
    assert not BuildPrinter(package_ahriman, is_success=True, use_utf=False).properties()


def test_sign_ascii(package_ahriman: Package) -> None:
    """
    must correctly generate sign in ascii
    """
    BuildPrinter(package_ahriman, is_success=True, use_utf=False).title().encode("ascii")
    BuildPrinter(package_ahriman, is_success=False, use_utf=False).title().encode("ascii")


def test_sign_utf8(package_ahriman: Package) -> None:
    """
    must correctly generate sign in ascii
    """
    with pytest.raises(UnicodeEncodeError):
        BuildPrinter(package_ahriman, is_success=True, use_utf=True).title().encode("ascii")
    with pytest.raises(UnicodeEncodeError):
        BuildPrinter(package_ahriman, is_success=False, use_utf=True).title().encode("ascii")


def test_title(package_ahriman: Package) -> None:
    """
    must return non empty title
    """
    assert BuildPrinter(package_ahriman, is_success=True, use_utf=False).title() is not None
