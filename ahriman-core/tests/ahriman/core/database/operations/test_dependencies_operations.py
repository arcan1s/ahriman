from ahriman.core.database import SQLite
from ahriman.models.dependencies import Dependencies
from ahriman.models.package import Package
from ahriman.models.repository_id import RepositoryId


def test_dependencies_insert_get(database: SQLite, package_ahriman: Package) -> None:
    """
    must insert and get dependencies
    """
    dependencies = Dependencies({"usr/lib/python3.11/site-packages": ["python"]})
    database.dependencies_insert(package_ahriman.base, dependencies)
    assert database.dependencies_get(package_ahriman.base) == {package_ahriman.base: dependencies}

    dependencies2 = Dependencies({"usr/lib/python3.11/site-packages": ["python3"]})
    database.dependencies_insert(
        package_ahriman.base, dependencies2, RepositoryId(
            "i686", database._repository_id.name))
    assert database.dependencies_get() == {package_ahriman.base: dependencies}
    assert database.dependencies_get(package_ahriman.base) == {package_ahriman.base: dependencies}
    assert database.dependencies_get(package_ahriman.base, RepositoryId("i686", database._repository_id.name)) == {
        package_ahriman.base: dependencies2
    }


def test_dependencies_insert_remove(database: SQLite, package_ahriman: Package,
                                    package_python_schedule: Package) -> None:
    """
    must remove dependencies for the package
    """
    dependencies1 = Dependencies({"usr": ["python"]})
    database.dependencies_insert(package_ahriman.base, dependencies1)
    dependencies2 = Dependencies({"usr": ["filesystem"]})
    database.dependencies_insert(package_python_schedule.base, dependencies2)
    dependencies3 = Dependencies({"usr": ["python3"]})
    database.dependencies_insert(
        package_ahriman.base, dependencies3, RepositoryId(
            "i686", database._repository_id.name))

    assert database.dependencies_get() == {
        package_ahriman.base: dependencies1,
        package_python_schedule.base: dependencies2,
    }

    database.dependencies_remove(package_ahriman.base)
    assert database.dependencies_get(package_ahriman.base) == {}
    assert database.dependencies_get(package_python_schedule.base) == {package_python_schedule.base: dependencies2}

    # insert null
    database.dependencies_remove(package_ahriman.base, RepositoryId("i686", database._repository_id.name))
    assert database.dependencies_get(package_ahriman.base, RepositoryId("i686", database._repository_id.name)) == {}
    assert database.dependencies_get(package_python_schedule.base) == {package_python_schedule.base: dependencies2}


def test_dependencies_insert_remove_full(database: SQLite, package_ahriman: Package,
                                         package_python_schedule: Package) -> None:
    """
    must remove all dependencies for the repository
    """
    database.dependencies_insert(package_ahriman.base, Dependencies({"usr": ["python"]}))
    database.dependencies_insert(package_python_schedule.base, Dependencies({"usr": ["filesystem"]}))
    database.dependencies_insert(package_ahriman.base, Dependencies({"usr": ["python3"]}),
                                 RepositoryId("i686", database._repository_id.name))

    database.dependencies_remove(None)
    assert database.dependencies_get() == {}
    assert database.dependencies_get(package_ahriman.base, RepositoryId("i686", database._repository_id.name))
