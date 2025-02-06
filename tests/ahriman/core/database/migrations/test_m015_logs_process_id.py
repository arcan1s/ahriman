from ahriman.core.database.migrations.m015_logs_process_id import steps


def test_migration_logs_process_id() -> None:
    """
    migration must not be empty
    """
    assert steps
