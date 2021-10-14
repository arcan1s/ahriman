from ahriman.models.smtp_ssl_settings import SmtpSSLSettings


def test_from_option_invalid() -> None:
    """
    must return disabled value on invalid option
    """
    assert SmtpSSLSettings.from_option("invalid") == SmtpSSLSettings.Disabled


def test_from_option_valid() -> None:
    """
    must return value from valid options
    """
    assert SmtpSSLSettings.from_option("ssl") == SmtpSSLSettings.SSL
    assert SmtpSSLSettings.from_option("SSL") == SmtpSSLSettings.SSL
    assert SmtpSSLSettings.from_option("ssl/tls") == SmtpSSLSettings.SSL
    assert SmtpSSLSettings.from_option("SSL/TLS") == SmtpSSLSettings.SSL

    assert SmtpSSLSettings.from_option("starttls") == SmtpSSLSettings.STARTTLS
    assert SmtpSSLSettings.from_option("STARTTLS") == SmtpSSLSettings.STARTTLS
