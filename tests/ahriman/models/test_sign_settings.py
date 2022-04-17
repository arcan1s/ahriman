from ahriman.models.sign_settings import SignSettings


def test_from_option_invalid() -> None:
    """
    must return disabled on invalid option
    """
    assert SignSettings.from_option("invalid") == SignSettings.Disabled


def test_from_option_valid() -> None:
    """
    must return value from valid options
    """
    assert SignSettings.from_option("package") == SignSettings.Packages
    assert SignSettings.from_option("PACKAGE") == SignSettings.Packages
    assert SignSettings.from_option("packages") == SignSettings.Packages
    assert SignSettings.from_option("sign-package") == SignSettings.Packages

    assert SignSettings.from_option("repository") == SignSettings.Repository
    assert SignSettings.from_option("REPOSITORY") == SignSettings.Repository
    assert SignSettings.from_option("sign-repository") == SignSettings.Repository
