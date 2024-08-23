from ahriman.core.database.migrations.m014_auditlog import steps


def test_migration_auditlog() -> None:
    """
    migration must not be empty
    """
    assert steps
