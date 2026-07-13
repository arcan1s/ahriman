from ahriman.core.database.migrations.m009_local_source import steps


def test_migration_local_source() -> None:
    """
    migration must not be empty
    """
    assert steps
