import pytest

from ahriman.core.exceptions import InvalidOption
from ahriman.models.auth_settings import AuthSettings


def test_from_option_invalid() -> None:
    """
    must raise exception on invalid option
    """
    with pytest.raises(InvalidOption, match=".* `invalid`$"):
        AuthSettings.from_option("invalid")


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


def test_is_enabled() -> None:
    """
    must mark as disabled authorization for disabled and enabled otherwise
    """
    assert not AuthSettings.Disabled.is_enabled
    for option in filter(lambda o: o != AuthSettings.Disabled, AuthSettings):
        assert option.is_enabled
