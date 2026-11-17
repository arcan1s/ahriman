from ahriman.models.sign_settings import SignSettings


def test_from_option_invalid() -> None:
    """
    must return disabled on invalid option
    """
    assert SignSettings.from_option("invalid") == SignSettings.DISABLED


def test_from_option_valid() -> None:
    """
    must return value from valid options
    """
    assert SignSettings.from_option("package") == SignSettings.PACKAGES
    assert SignSettings.from_option("PACKAGE") == SignSettings.PACKAGES
    assert SignSettings.from_option("packages") == SignSettings.PACKAGES
    assert SignSettings.from_option("sign-package") == SignSettings.PACKAGES

    assert SignSettings.from_option("repository") == SignSettings.REPOSITORY
    assert SignSettings.from_option("REPOSITORY") == SignSettings.REPOSITORY
    assert SignSettings.from_option("sign-repository") == SignSettings.REPOSITORY
