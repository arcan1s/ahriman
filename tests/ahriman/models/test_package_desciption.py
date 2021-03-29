from unittest.mock import MagicMock

from ahriman.models.package_description import PackageDescription


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


def test_from_package(package_description_ahriman: PackageDescription,
                      pyalpm_package_description_ahriman: MagicMock) -> None:
    """
    must construct description from package object
    """
    package_description = PackageDescription.from_package(pyalpm_package_description_ahriman,
                                                          package_description_ahriman.filepath)
    assert package_description_ahriman == package_description
