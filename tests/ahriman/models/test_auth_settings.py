from ahriman.models.auth_settings import AuthSettings


def test_from_option_invalid() -> None:
    """
    return disabled on invalid option
    """
    assert AuthSettings.from_option("invalid") == AuthSettings.Disabled


def test_from_option_valid() -> None:
    """
    must return value from valid options
    """
    assert AuthSettings.from_option("disabled") == AuthSettings.Disabled
    assert AuthSettings.from_option("DISABLED") == AuthSettings.Disabled
    assert AuthSettings.from_option("no") == AuthSettings.Disabled
    assert AuthSettings.from_option("NO") == AuthSettings.Disabled

    assert AuthSettings.from_option("oauth") == AuthSettings.OAuth
    assert AuthSettings.from_option("OAuth") == AuthSettings.OAuth
    assert AuthSettings.from_option("OAuth2") == AuthSettings.OAuth

    assert AuthSettings.from_option("configuration") == AuthSettings.Configuration
    assert AuthSettings.from_option("ConFigUration") == AuthSettings.Configuration
    assert AuthSettings.from_option("mapping") == AuthSettings.Configuration
    assert AuthSettings.from_option("MAPPing") == AuthSettings.Configuration

    assert AuthSettings.from_option("pam") == AuthSettings.PAM
    assert AuthSettings.from_option("PAM") == AuthSettings.PAM


def test_is_enabled() -> None:
    """
    must mark as disabled authorization for disabled and enabled otherwise
    """
    assert not AuthSettings.Disabled.is_enabled
    for option in filter(lambda o: o != AuthSettings.Disabled, AuthSettings):
        assert option.is_enabled
