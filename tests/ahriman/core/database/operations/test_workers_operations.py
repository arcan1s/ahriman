from ahriman.core.database import SQLite
from ahriman.models.worker import Worker


def test_workers_get_insert(database: SQLite) -> None:
    """
    must insert workers to database
    """
    database.workers_insert(Worker("address1", identifier="1"))
    database.workers_insert(Worker("address2", identifier="2"))
    assert database.workers_get() == [
        Worker("address1", identifier="1"), Worker("address2", identifier="2")
    ]


def test_workers_insert_remove(database: SQLite) -> None:
    """
    must remove worker from database
    """
    database.workers_insert(Worker("address1", identifier="1"))
    database.workers_insert(Worker("address2", identifier="2"))
    database.workers_remove("1")

    assert database.workers_get() == [Worker("address2", identifier="2")]


def test_workers_insert_remove_all(database: SQLite) -> None:
    """
    must remove all workers
    """
    database.workers_insert(Worker("address1", identifier="1"))
    database.workers_insert(Worker("address2", identifier="2"))
    database.workers_remove()

    assert database.workers_get() == []


def test_workers_insert_insert(database: SQLite) -> None:
    """
    must update worker in database
    """
    database.workers_insert(Worker("address1", identifier="1"))
    assert database.workers_get() == [Worker("address1", identifier="1")]

    database.workers_insert(Worker("address2", identifier="1"))
    assert database.workers_get() == [Worker("address2", identifier="1")]
