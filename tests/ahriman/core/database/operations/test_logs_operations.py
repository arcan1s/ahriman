from ahriman.core.database import SQLite
from ahriman.models.log_record_id import LogRecordId
from ahriman.models.package import Package


def test_logs_insert_remove_process(database: SQLite, package_ahriman: Package,
                                    package_python_schedule: Package) -> None:
    """
    must clear process specific package logs
    """
    database.logs_insert(LogRecordId(package_ahriman.base, 1), 42.0, "message 1")
    database.logs_insert(LogRecordId(package_ahriman.base, 2), 43.0, "message 2")
    database.logs_insert(LogRecordId(package_python_schedule.base, 1), 42.0, "message 3")

    database.logs_remove(package_ahriman.base, 1)
    assert database.logs_get(package_ahriman.base) == "[1970-01-01 00:00:42] message 1"
    assert database.logs_get(package_python_schedule.base) == "[1970-01-01 00:00:42] message 3"


def test_logs_insert_remove_full(database: SQLite, package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must clear full package logs
    """
    database.logs_insert(LogRecordId(package_ahriman.base, 1), 42.0, "message 1")
    database.logs_insert(LogRecordId(package_ahriman.base, 2), 43.0, "message 2")
    database.logs_insert(LogRecordId(package_python_schedule.base, 1), 42.0, "message 3")

    database.logs_remove(package_ahriman.base, None)
    assert not database.logs_get(package_ahriman.base)
    assert database.logs_get(package_python_schedule.base) == "[1970-01-01 00:00:42] message 3"


def test_logs_insert_get(database: SQLite, package_ahriman: Package) -> None:
    """
    must insert and get package logs
    """
    database.logs_insert(LogRecordId(package_ahriman.base, 1), 43.0, "message 2")
    database.logs_insert(LogRecordId(package_ahriman.base, 1), 42.0, "message 1")
    assert database.logs_get(package_ahriman.base) == "[1970-01-01 00:00:42] message 1\n[1970-01-01 00:00:43] message 2"
