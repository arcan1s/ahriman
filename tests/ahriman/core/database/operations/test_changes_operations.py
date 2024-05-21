from ahriman.core.database import SQLite
from ahriman.models.changes import Changes
from ahriman.models.package import Package
from ahriman.models.repository_id import RepositoryId


def test_changes_insert_get(database: SQLite, package_ahriman: Package) -> None:
    """
    must insert and get changes
    """
    database.changes_insert(package_ahriman.base, Changes("sha1", "change1"))
    assert database.changes_get(package_ahriman.base).changes == "change1"

    database.changes_insert(package_ahriman.base, Changes("sha2", "change2"),
                            RepositoryId("i686", database._repository_id.name))
    assert database.changes_get(package_ahriman.base).changes == "change1"
    assert database.changes_get(
        package_ahriman.base, RepositoryId("i686", database._repository_id.name)).changes == "change2"


def test_changes_insert_remove(database: SQLite, package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must remove changes for the package
    """
    database.changes_insert(package_ahriman.base, Changes("sha1", "change1"))
    database.changes_insert(package_python_schedule.base, Changes("sha3", "change3"))
    database.changes_insert(package_ahriman.base, Changes("sha2", "change2"),
                            RepositoryId("i686", database._repository_id.name))

    database.changes_remove(package_ahriman.base)
    assert database.changes_get(package_ahriman.base).changes is None
    assert database.changes_get(package_python_schedule.base).changes == "change3"

    # insert null
    database.changes_insert(package_ahriman.base, Changes(), RepositoryId("i686", database._repository_id.name))
    assert database.changes_get(
        package_ahriman.base, RepositoryId("i686", database._repository_id.name)).changes is None
    assert database.changes_get(package_python_schedule.base).changes == "change3"


def test_changes_insert_remove_full(database: SQLite, package_ahriman: Package,
                                    package_python_schedule: Package) -> None:
    """
    must remove all changes for the repository
    """
    database.changes_insert(package_ahriman.base, Changes("sha1", "change1"))
    database.changes_insert(package_python_schedule.base, Changes("sha3", "change3"))
    database.changes_insert(package_ahriman.base, Changes("sha2", "change2"),
                            RepositoryId("i686", database._repository_id.name))

    database.changes_remove(None)
    assert database.changes_get(package_ahriman.base).changes is None
    assert database.changes_get(package_python_schedule.base).changes is None
    assert database.changes_get(
        package_ahriman.base, RepositoryId("i686", database._repository_id.name)).changes == "change2"
