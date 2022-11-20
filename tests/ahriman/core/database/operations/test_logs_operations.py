from ahriman.core.database import SQLite
from ahriman.models.package import Package


def test_logs_insert_delete(database: SQLite, package_ahriman: Package, package_python_schedule: Package) -> None:
    """
    must clear all packages
    """
    database.logs_insert(package_ahriman.base, 0.001, "message 1")
    database.logs_insert(package_python_schedule.base, 0.002, "message 2")

    database.logs_delete(package_ahriman.base)
    assert not database.logs_get(package_ahriman.base)
    assert database.logs_get(package_python_schedule.base)


def test_logs_insert_get(database: SQLite, package_ahriman: Package) -> None:
    """
    must insert and get package logs
    """
    database.logs_insert(package_ahriman.base, 0.002, "message 2")
    database.logs_insert(package_ahriman.base, 0.001, "message 1")
    assert database.logs_get(package_ahriman.base) == "message 1\nmessage 2"
