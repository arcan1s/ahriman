from ahriman.core.database.migrations.m000_initial import steps


def test_migration_initial() -> None:
    """
    migration must not be empty
    """
    assert steps
