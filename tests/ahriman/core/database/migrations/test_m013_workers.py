from ahriman.core.database.migrations.m013_workers import steps


def test_migration_workers() -> None:
    """
    migration must not be empty
    """
    assert steps
