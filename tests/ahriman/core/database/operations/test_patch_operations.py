from ahriman.core.database.sqlite import SQLite
from ahriman.models.package import Package


def test_patches_get_insert(database: SQLite, package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must insert patch to database
    """
    database.patches_insert(package_ahriman.base, "patch_1")
    database.patches_insert(package_python_schedule.base, "patch_2")
    assert database.patches_get(package_ahriman.base) == "patch_1"
    assert not database.build_queue_get()


def test_patches_list(database: SQLite, package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must list all patches
    """
    database.patches_insert(package_ahriman.base, "patch1")
    database.patches_insert(package_python_schedule.base, "patch2")
    assert database.patches_list(None) == {package_ahriman.base: "patch1", package_python_schedule.base: "patch2"}


def test_patches_list_filter(database: SQLite, package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must list all patches filtered by package name (same as get)
    """
    database.patches_insert(package_ahriman.base, "patch1")
    database.patches_insert(package_python_schedule.base, "patch2")

    assert database.patches_list(package_ahriman.base) == {package_ahriman.base: "patch1"}
    assert database.patches_list(package_python_schedule.base) == {package_python_schedule.base: "patch2"}


def test_patches_insert_remove(database: SQLite, package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must remove patch from database
    """
    database.patches_insert(package_ahriman.base, "patch_1")
    database.patches_insert(package_python_schedule.base, "patch_2")
    database.patches_remove(package_ahriman.base)

    assert database.patches_get(package_ahriman.base) is None
    database.patches_insert(package_python_schedule.base, "patch_2")


def test_patches_insert_insert(database: SQLite, package_ahriman: Package) -> None:
    """
    must update patch in database
    """
    database.patches_insert(package_ahriman.base, "patch_1")
    assert database.patches_get(package_ahriman.base) == "patch_1"

    database.patches_insert(package_ahriman.base, "patch_2")
    assert database.patches_get(package_ahriman.base) == "patch_2"
