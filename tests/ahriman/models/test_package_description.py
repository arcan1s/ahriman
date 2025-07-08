from unittest.mock import MagicMock

from ahriman.models.aur_package import AURPackage
from ahriman.models.package_description import PackageDescription


def test_post_init() -> None:
    """
    must trim versions and descriptions from packages list
    """
    assert PackageDescription(
        depends=["a=1"],
        make_depends=["b>=3"],
        opt_depends=["c: a description"],
        check_depends=["d=4"],
        provides=["e=5"]
    ) == PackageDescription(depends=["a"], make_depends=["b"], opt_depends=["c"], check_depends=["d"], provides=["e"])


def test_filepath(package_description_ahriman: PackageDescription) -> None:
    """
    must generate correct filepath if set
    """
    assert package_description_ahriman.filepath is not None
    assert package_description_ahriman.filepath.name == package_description_ahriman.filename


def test_filepath_empty(package_description_ahriman: PackageDescription) -> None:
    """
    must return None for missing filename
    """
    package_description_ahriman.filename = None
    assert package_description_ahriman.filepath is None


def test_from_aur(package_description_ahriman: PackageDescription, aur_package_ahriman: AURPackage) -> None:
    """
    must construct package description from AUR descriptor
    """
    actual = PackageDescription.from_aur(aur_package_ahriman)
    # missing attributes
    actual.architecture = package_description_ahriman.architecture
    actual.archive_size = package_description_ahriman.archive_size
    actual.build_date = package_description_ahriman.build_date
    actual.filename = package_description_ahriman.filename
    actual.installed_size = package_description_ahriman.installed_size


def test_from_json(package_description_ahriman: PackageDescription) -> None:
    """
    must construct description from json object
    """
    assert PackageDescription.from_json(package_description_ahriman.view()) == package_description_ahriman


def test_from_json_with_unknown_fields(package_description_ahriman: PackageDescription) -> None:
    """
    must construct description from json object containing unknown fields
    """
    dump = package_description_ahriman.view()
    dump.update(unknown_field="value")
    assert PackageDescription.from_json(dump) == package_description_ahriman


def test_from_package(package_description_ahriman: PackageDescription,
                      pyalpm_package_description_ahriman: MagicMock) -> None:
    """
    must construct description from package object
    """
    package_description = PackageDescription.from_package(pyalpm_package_description_ahriman,
                                                          package_description_ahriman.filepath)
    assert package_description_ahriman == package_description


def test_from_json_view(package_description_ahriman: PackageDescription) -> None:
    """
    must generate same description from json view
    """
    assert PackageDescription.from_json(package_description_ahriman.view()) == package_description_ahriman
