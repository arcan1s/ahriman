from ahriman.core.database.migrations.m001_package_source import steps


def test_migration_package_source() -> None:
    """
    migration must not be empty
    """
    assert steps
