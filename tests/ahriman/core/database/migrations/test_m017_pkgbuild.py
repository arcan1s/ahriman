from ahriman.core.database.migrations.m017_pkgbuild import steps


def test_migration_pkgbuild() -> None:
    """
    migration must not be empty
    """
    assert steps
