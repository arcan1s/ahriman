import smtplib

import pytest

from pytest_mock import MockerFixture

from ahriman.core.configuration import Configuration
from ahriman.core.report.email import Email
from ahriman.models.package import Package
from ahriman.models.result import Result
from ahriman.models.smtp_ssl_settings import SmtpSSLSettings


def test_template(configuration: Configuration) -> None:
    """
    must correctly parse template name and path
    """
    template = configuration.get("email", "template")
    root, repository_id = configuration.check_loaded()

    assert Email(repository_id, configuration, "email").template == template

    configuration.remove_option("email", "template")
    configuration.set_option("email", "template_path", template)
    assert Email(repository_id, configuration, "email").template == root.parent / template


def test_template_full(configuration: Configuration) -> None:
    """
    must correctly parse full template name and path
    """
    template = "template"
    root, repository_id = configuration.check_loaded()

    configuration.set_option("email", "template_full", template)
    assert Email(repository_id, configuration, "email").template_full == template

    configuration.remove_option("email", "template_full")
    configuration.set_option("email", "full_template_path", template)
    assert Email(repository_id, configuration, "email").template_full == root.parent / template


def test_smtp_session(email: Email) -> None:
    """
    must build normal SMTP session if SSL is disabled
    """
    email.ssl = SmtpSSLSettings.Disabled
    assert email._smtp_session == smtplib.SMTP

    email.ssl = SmtpSSLSettings.STARTTLS
    assert email._smtp_session == smtplib.SMTP


def test_smtp_session_ssl(email: Email) -> None:
    """
    must build SMTP_SSL session if SSL is enabled
    """
    email.ssl = SmtpSSLSettings.SSL
    assert email._smtp_session == smtplib.SMTP_SSL


def test_send(email: Email, mocker: MockerFixture) -> None:
    """
    must send an email with attachment
    """
    smtp_mock = mocker.patch("smtplib.SMTP")
    smtp_mock.return_value.__enter__.return_value = smtp_mock.return_value

    email._send("a text", {"attachment.html": "an attachment"})
    smtp_mock.return_value.starttls.assert_not_called()
    smtp_mock.return_value.login.assert_not_called()
    smtp_mock.return_value.sendmail.assert_called_once_with(email.sender, email.receivers, pytest.helpers.anyvar(int))


def test_send_auth(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must send an email with attachment with auth
    """
    configuration.set_option("email", "user", "username")
    configuration.set_option("email", "password", "password")
    smtp_mock = mocker.patch("smtplib.SMTP")
    smtp_mock.return_value.__enter__.return_value = smtp_mock.return_value
    _, repository_id = configuration.check_loaded()

    email = Email(repository_id, configuration, "email")
    email._send("a text", {"attachment.html": "an attachment"})
    smtp_mock.return_value.login.assert_called_once_with(email.user, email.password)


def test_send_auth_no_password(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must send an email with attachment without auth if no password supplied
    """
    configuration.set_option("email", "user", "username")
    smtp_mock = mocker.patch("smtplib.SMTP")
    smtp_mock.return_value.__enter__.return_value = smtp_mock.return_value
    _, repository_id = configuration.check_loaded()

    email = Email(repository_id, configuration, "email")
    email._send("a text", {"attachment.html": "an attachment"})
    smtp_mock.return_value.login.assert_not_called()


def test_send_auth_no_user(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must send an email with attachment without auth if no user supplied
    """
    configuration.set_option("email", "password", "password")
    smtp_mock = mocker.patch("smtplib.SMTP")
    smtp_mock.return_value.__enter__.return_value = smtp_mock.return_value
    _, repository_id = configuration.check_loaded()

    email = Email(repository_id, configuration, "email")
    email._send("a text", {"attachment.html": "an attachment"})
    smtp_mock.return_value.login.assert_not_called()


def test_send_ssl_tls(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must send an email with attachment with ssl/tls
    """
    configuration.set_option("email", "ssl", "ssl")
    smtp_mock = mocker.patch("smtplib.SMTP_SSL")
    smtp_mock.return_value.__enter__.return_value = smtp_mock.return_value
    _, repository_id = configuration.check_loaded()

    email = Email(repository_id, configuration, "email")
    email._send("a text", {"attachment.html": "an attachment"})
    smtp_mock.return_value.starttls.assert_not_called()
    smtp_mock.return_value.login.assert_not_called()
    smtp_mock.return_value.sendmail.assert_called_once_with(email.sender, email.receivers, pytest.helpers.anyvar(int))


def test_send_starttls(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must send an email with attachment with starttls
    """
    configuration.set_option("email", "ssl", "starttls")
    smtp_mock = mocker.patch("smtplib.SMTP")
    smtp_mock.return_value.__enter__.return_value = smtp_mock.return_value
    _, repository_id = configuration.check_loaded()

    email = Email(repository_id, configuration, "email")
    email._send("a text", {"attachment.html": "an attachment"})
    smtp_mock.return_value.starttls.assert_called_once_with()


def test_generate(email: Email, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must generate report
    """
    send_mock = mocker.patch("ahriman.core.report.email.Email._send")
    email.generate([package_ahriman], Result())
    send_mock.assert_called_once_with(pytest.helpers.anyvar(int), {})


def test_generate_with_built(email: Email, package_ahriman: Package, result: Result, mocker: MockerFixture) -> None:
    """
    must generate report with built packages
    """
    send_mock = mocker.patch("ahriman.core.report.email.Email._send")
    email.generate([package_ahriman], result)
    send_mock.assert_called_once_with(pytest.helpers.anyvar(int), {})


def test_generate_with_built_and_full_path(email: Email, package_ahriman: Package, result: Result,
                                           mocker: MockerFixture) -> None:
    """
    must generate report with built packages and full packages lists
    """
    send_mock = mocker.patch("ahriman.core.report.email.Email._send")

    email.template_full = email.template
    email.generate([package_ahriman], result)
    send_mock.assert_called_once_with(pytest.helpers.anyvar(int), pytest.helpers.anyvar(int))


def test_generate_no_empty(configuration: Configuration, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must not generate report with built packages if no_empty_report is set
    """
    configuration.set_option("email", "no_empty_report", "yes")
    send_mock = mocker.patch("ahriman.core.report.email.Email._send")
    _, repository_id = configuration.check_loaded()

    email = Email(repository_id, configuration, "email")
    email.generate([package_ahriman], Result())
    send_mock.assert_not_called()


def test_generate_no_empty_with_built(configuration: Configuration, package_ahriman: Package, result: Result,
                                      mocker: MockerFixture) -> None:
    """
    must generate report with built packages if no_empty_report is set
    """
    configuration.set_option("email", "no_empty_report", "yes")
    send_mock = mocker.patch("ahriman.core.report.email.Email._send")
    _, repository_id = configuration.check_loaded()

    email = Email(repository_id, configuration, "email")
    email.generate([package_ahriman], result)
    send_mock.assert_called_once_with(pytest.helpers.anyvar(int), {})
