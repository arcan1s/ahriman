from ahriman.core.database.migrations.m002_user_access import steps


def test_migration_package_source() -> None:
    """
    migration must not be empty
    """
    assert steps
