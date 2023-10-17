from ahriman.core.database import SQLite
from ahriman.models.log_record_id import LogRecordId
from ahriman.models.package import Package
from ahriman.models.repository_id import RepositoryId


def test_logs_insert_remove_version(database: SQLite, package_ahriman: Package,
                                    package_python_schedule: Package) -> None:
    """
    must clear version specific package logs
    """
    database.logs_insert(LogRecordId(package_ahriman.base, "1"), 42.0, "message 1")
    database.logs_insert(LogRecordId(package_ahriman.base, "2"), 43.0, "message 2")
    database.logs_insert(LogRecordId(package_python_schedule.base, "1"), 42.0, "message 3")

    database.logs_remove(package_ahriman.base, "1")
    assert database.logs_get(package_ahriman.base) == [(42.0, "message 1")]
    assert database.logs_get(package_python_schedule.base) == [(42.0, "message 3")]


def test_logs_insert_remove_multi(database: SQLite, package_ahriman: Package) -> None:
    """
    must clear logs for specified repository
    """
    database.logs_insert(LogRecordId(package_ahriman.base, "1"), 42.0, "message 1")
    database.logs_insert(LogRecordId(package_ahriman.base, "1"), 43.0, "message 2",
                         RepositoryId("i686", database._repository_id.name))

    database.logs_remove(package_ahriman.base, None, RepositoryId("i686", database._repository_id.name))
    assert not database.logs_get(package_ahriman.base, repository_id=RepositoryId("i686", database._repository_id.name))
    assert database.logs_get(package_ahriman.base) == [(42.0, "message 1")]


def test_logs_insert_remove_full(database: SQLite, package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must clear full package logs
    """
    database.logs_insert(LogRecordId(package_ahriman.base, "1"), 42.0, "message 1")
    database.logs_insert(LogRecordId(package_ahriman.base, "2"), 43.0, "message 2")
    database.logs_insert(LogRecordId(package_python_schedule.base, "1"), 42.0, "message 3")

    database.logs_remove(package_ahriman.base, None)
    assert not database.logs_get(package_ahriman.base)
    assert database.logs_get(package_python_schedule.base) == [(42.0, "message 3")]


def test_logs_insert_get(database: SQLite, package_ahriman: Package) -> None:
    """
    must insert and get package logs
    """
    database.logs_insert(LogRecordId(package_ahriman.base, "1"), 43.0, "message 2")
    database.logs_insert(LogRecordId(package_ahriman.base, "1"), 42.0, "message 1")
    assert database.logs_get(package_ahriman.base) == [(42.0, "message 1"), (43.0, "message 2")]


def test_logs_insert_get_pagination(database: SQLite, package_ahriman: Package) -> None:
    """
    must insert and get package logs with pagination
    """
    database.logs_insert(LogRecordId(package_ahriman.base, "1"), 42.0, "message 1")
    database.logs_insert(LogRecordId(package_ahriman.base, "1"), 43.0, "message 2")
    assert database.logs_get(package_ahriman.base, 1, 1) == [(43.0, "message 2")]


def test_logs_insert_get_multi(database: SQLite, package_ahriman: Package) -> None:
    """
    must insert and get package logs for multiple repositories
    """
    database.logs_insert(LogRecordId(package_ahriman.base, "1"), 42.0, "message 1")
    database.logs_insert(LogRecordId(package_ahriman.base, "1"), 43.0, "message 2",
                         RepositoryId("i686", database._repository_id.name))

    assert database.logs_get(package_ahriman.base,
                             repository_id=RepositoryId("i686", database._repository_id.name)) == [(43.0, "message 2")]
    assert database.logs_get(package_ahriman.base) == [(42.0, "message 1")]
