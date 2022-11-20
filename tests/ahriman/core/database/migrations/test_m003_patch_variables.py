from ahriman.core.database.migrations.m003_patch_variables import steps


def test_migration_patches() -> None:
    """
    migration must not be empty
    """
    assert steps
