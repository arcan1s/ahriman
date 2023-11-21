from ahriman.core.database.migrations.m012_last_commit_sha import steps


def test_migration_last_commit_sha() -> None:
    """
    migration must not be empty
    """
    assert steps
