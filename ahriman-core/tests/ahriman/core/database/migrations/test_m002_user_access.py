from ahriman.core.database.migrations.m002_user_access import steps


def test_migration_user_access() -> None:
    """
    migration must not be empty
    """
    assert steps
