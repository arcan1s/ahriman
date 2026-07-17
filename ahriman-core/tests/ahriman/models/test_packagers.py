from ahriman.models.package import Package
from ahriman.models.packagers import Packagers


def test_for_base(package_ahriman: Package) -> None:
    """
    must return username used for base package
    """
    assert Packagers(None, {package_ahriman.base: "packager"}).for_base(package_ahriman.base) == "packager"
    assert Packagers("default", {package_ahriman.base: "packager"}).for_base("random") == "default"
    assert Packagers("default").for_base(package_ahriman.base) == "default"
    assert Packagers().for_base(package_ahriman.base) is None
