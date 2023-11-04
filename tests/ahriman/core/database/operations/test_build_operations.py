from ahriman.core.database import SQLite
from ahriman.models.package import Package
from ahriman.models.repository_id import RepositoryId


def test_build_queue_insert_clear(database: SQLite, package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must clear all packages from queue
    """
    database.build_queue_insert(package_ahriman)
    database.build_queue_insert(package_python_schedule)

    database.build_queue_clear(None)
    assert not database.build_queue_get()


def test_build_queue_insert_clear_multi(database: SQLite, package_ahriman: Package) -> None:
    """
    must clear all packages from queue for specific repository
    """
    database.build_queue_insert(package_ahriman)
    database.build_queue_insert(package_ahriman, RepositoryId("i686", database._repository_id.name))

    database.build_queue_clear(None)
    assert database.build_queue_get(RepositoryId("i686", database._repository_id.name)) == [package_ahriman]


def test_build_queue_insert_clear_specific(database: SQLite, package_ahriman: Package,
                                           package_python_schedule: Package) -> None:
    """
    must remove only specified package from the queue
    """
    database.build_queue_insert(package_ahriman)
    database.build_queue_insert(package_python_schedule)

    database.build_queue_clear(package_python_schedule.base)
    assert database.build_queue_get() == [package_ahriman]


def test_build_queue_insert_get(database: SQLite, package_ahriman: Package) -> None:
    """
    must insert and get package from the database
    """
    database.build_queue_insert(package_ahriman)
    assert database.build_queue_get() == [package_ahriman]


def test_build_queue_insert(database: SQLite, package_ahriman: Package) -> None:
    """
    must update build queue in the database
    """
    database.build_queue_insert(package_ahriman)
    assert database.build_queue_get() == [package_ahriman]

    package_ahriman.version = "42"
    database.build_queue_insert(package_ahriman)
    assert database.build_queue_get() == [package_ahriman]


def test_build_queue_insert_multi(database: SQLite, package_ahriman: Package) -> None:
    """
    must update build queue in the database for multiple architectures and repositories
    """
    package_ahriman.version = "1"
    database.build_queue_insert(package_ahriman)
    assert database.build_queue_get() == [package_ahriman]

    package_ahriman.version = "2"
    database.build_queue_insert(package_ahriman, RepositoryId("i686", database._repository_id.name))
    assert database.build_queue_get(RepositoryId("i686", database._repository_id.name)) == [package_ahriman]

    package_ahriman.version = "1"
    assert database.build_queue_get(RepositoryId("x86_64", database._repository_id.name)) == [package_ahriman]

    package_ahriman.version = "3"
    database.build_queue_insert(package_ahriman, RepositoryId(database._repository_id.architecture, "repo"))
    assert database.build_queue_get(RepositoryId(database._repository_id.architecture, "repo")) == [package_ahriman]

    package_ahriman.version = "1"
    assert database.build_queue_get() == [package_ahriman]
