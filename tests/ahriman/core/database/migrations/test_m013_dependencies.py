from ahriman.core.database.migrations.m013_dependencies import steps


def test_migration_dependencies() -> None:
    """
    migration must not be empty
    """
    assert steps
