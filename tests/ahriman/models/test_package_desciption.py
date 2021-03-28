from ahriman.models.package_desciption import PackageDescription


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
