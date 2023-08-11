from ahriman.core.database.migrations.m009_local_source import steps


def test_migration_packagers() -> None:
    """
    migration must not be empty
    """
    assert steps
