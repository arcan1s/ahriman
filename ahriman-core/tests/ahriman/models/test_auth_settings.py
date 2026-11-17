from ahriman.models.auth_settings import AuthSettings


def test_from_option_invalid() -> None:
    """
    return disabled on invalid option
    """
    assert AuthSettings.from_option("invalid") == AuthSettings.DISABLED


def test_from_option_valid() -> None:
    """
    must return value from valid options
    """
    assert AuthSettings.from_option("disabled") == AuthSettings.DISABLED
    assert AuthSettings.from_option("DISABLED") == AuthSettings.DISABLED
    assert AuthSettings.from_option("no") == AuthSettings.DISABLED
    assert AuthSettings.from_option("NO") == AuthSettings.DISABLED

    assert AuthSettings.from_option("oauth") == AuthSettings.OAUTH
    assert AuthSettings.from_option("OAuth") == AuthSettings.OAUTH
    assert AuthSettings.from_option("OAuth2") == AuthSettings.OAUTH

    assert AuthSettings.from_option("configuration") == AuthSettings.CONFIGURATION
    assert AuthSettings.from_option("ConFigUration") == AuthSettings.CONFIGURATION
    assert AuthSettings.from_option("mapping") == AuthSettings.CONFIGURATION
    assert AuthSettings.from_option("MAPPing") == AuthSettings.CONFIGURATION

    assert AuthSettings.from_option("pam") == AuthSettings.PAM
    assert AuthSettings.from_option("PAM") == AuthSettings.PAM


def test_is_enabled() -> None:
    """
    must mark as disabled authorization for disabled and enabled otherwise
    """
    assert not AuthSettings.DISABLED.is_enabled
    for option in filter(lambda o: o != AuthSettings.DISABLED, AuthSettings):
        assert option.is_enabled
