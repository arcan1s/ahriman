import ahriman.version as version


def test_version() -> None:
    """
    version must not be empty
    """
    assert getattr(version, "__version__")
