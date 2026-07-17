from ahriman.core.database.migrations.m004_logs import steps


def test_migration_logs() -> None:
    """
    migration must not be empty
    """
    assert steps
