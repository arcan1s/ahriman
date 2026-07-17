from ahriman.core.database.migrations.m018_package_hold import steps


def test_migration_package_hold() -> None:
    """
    migration must not be empty
    """
    assert steps
