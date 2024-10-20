from ahriman.core.database import SQLite
from ahriman.models.package import Package
from ahriman.models.pkgbuild_patch import PkgbuildPatch


def test_patches_get_insert(database: SQLite, package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must insert patch to database
    """
    database.patches_insert(package_ahriman.base, [PkgbuildPatch(None, "patch_1")])
    database.patches_insert(package_ahriman.base, [PkgbuildPatch("key", "patch_3")])
    database.patches_insert(package_python_schedule.base, [PkgbuildPatch(None, "patch_2")])
    assert database.patches_get(package_ahriman.base) == [
        PkgbuildPatch(None, "patch_1"), PkgbuildPatch("key", "patch_3")
    ]


def test_patches_list(database: SQLite, package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must list all patches
    """
    database.patches_insert(package_ahriman.base, [PkgbuildPatch(None, "patch1")])
    database.patches_insert(package_ahriman.base, [PkgbuildPatch("key", "patch3")])
    database.patches_insert(package_python_schedule.base, [PkgbuildPatch(None, "patch2")])
    assert database.patches_list(None, None) == {
        package_ahriman.base: [PkgbuildPatch(None, "patch1"), PkgbuildPatch("key", "patch3")],
        package_python_schedule.base: [PkgbuildPatch(None, "patch2")],
    }


def test_patches_list_filter(database: SQLite, package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must list all patches filtered by package name (same as get)
    """
    database.patches_insert(package_ahriman.base, [PkgbuildPatch(None, "patch1")])
    database.patches_insert(package_python_schedule.base, [PkgbuildPatch(None, "patch2")])

    assert database.patches_list(package_ahriman.base, None) == {package_ahriman.base: [PkgbuildPatch(None, "patch1")]}
    assert database.patches_list(package_python_schedule.base, None) == {
        package_python_schedule.base: [PkgbuildPatch(None, "patch2")],
    }


def test_patches_list_filter_by_variable(database: SQLite, package_ahriman: Package,
                                         package_python_schedule: Package) -> None:
    """
    must list all patches filtered by variable (same as get)
    """
    database.patches_insert(package_ahriman.base, [PkgbuildPatch(None, "patch1")])
    database.patches_insert(package_ahriman.base, [PkgbuildPatch("key", "patch2")])
    database.patches_insert(package_python_schedule.base, [PkgbuildPatch(None, "patch3")])

    assert database.patches_list(None, None) == {
        package_ahriman.base: [PkgbuildPatch(None, "patch1"), PkgbuildPatch("key", "patch2")],
        package_python_schedule.base: [PkgbuildPatch(None, "patch3")],
    }
    assert database.patches_list(None, ["key"]) == {
        package_ahriman.base: [PkgbuildPatch("key", "patch2")],
    }


def test_patches_insert_remove(database: SQLite, package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must remove patch from database
    """
    database.patches_insert(package_ahriman.base, [PkgbuildPatch(None, "patch1")])
    database.patches_insert(package_python_schedule.base, [PkgbuildPatch(None, "patch2")])
    database.patches_remove(package_ahriman.base, None)

    assert database.patches_get(package_ahriman.base) == []
    assert database.patches_get(package_python_schedule.base) == [PkgbuildPatch(None, "patch2")]


def test_patches_insert_remove_by_variable(database: SQLite, package_ahriman: Package,
                                           package_python_schedule: Package) -> None:
    """
    must remove patch from database by variable
    """
    database.patches_insert(package_ahriman.base, [PkgbuildPatch(None, "patch1")])
    database.patches_insert(package_ahriman.base, [PkgbuildPatch("key", "patch3")])
    database.patches_insert(package_python_schedule.base, [PkgbuildPatch(None, "patch2")])
    database.patches_remove(package_ahriman.base, ["key"])

    assert database.patches_get(package_ahriman.base) == [PkgbuildPatch(None, "patch1")]
    assert database.patches_get(package_python_schedule.base) == [PkgbuildPatch(None, "patch2")]


def test_patches_insert_insert(database: SQLite, package_ahriman: Package) -> None:
    """
    must update patch in database
    """
    database.patches_insert(package_ahriman.base, [PkgbuildPatch(None, "patch1")])
    assert database.patches_get(package_ahriman.base) == [PkgbuildPatch(None, "patch1")]

    database.patches_insert(package_ahriman.base, [PkgbuildPatch(None, "patch2")])
    assert database.patches_get(package_ahriman.base) == [PkgbuildPatch(None, "patch2")]

    database.patches_insert(package_ahriman.base, [PkgbuildPatch(None, "patch3"), PkgbuildPatch("key", "patch4")])
    assert database.patches_get(package_ahriman.base) == [
        PkgbuildPatch(None, "patch3"),
        PkgbuildPatch("key", "patch4"),
    ]
