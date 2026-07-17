from ahriman.core.database.migrations.m010_version_based_logs_removal import steps


def test_migration_version_based_logs_removal() -> None:
    """
    migration must not be empty
    """
    assert steps
