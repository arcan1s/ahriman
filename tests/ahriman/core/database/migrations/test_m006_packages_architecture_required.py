from ahriman.core.database.migrations.m006_packages_architecture_required import steps


def test_migration_logs() -> None:
    """
    migration must not be empty
    """
    assert steps
