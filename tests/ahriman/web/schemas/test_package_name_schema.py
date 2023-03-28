from ahriman.models.package import Package
from ahriman.web.schemas.package_name_schema import PackageNameSchema


def test_schema(package_ahriman: Package) -> None:
    """
    must return valid schema
    """
    schema = PackageNameSchema()
    assert not schema.validate({"package": package_ahriman.base})
