import pytest
import requests

from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.core.configuration import Configuration
from ahriman.core.report.telegram import Telegram
from ahriman.models.package import Package
from ahriman.models.result import Result


def test_send(telegram: Telegram, mocker: MockerFixture) -> None:
    """
    must send a message
    """
    request_mock = mocker.patch("ahriman.core.report.telegram.Telegram.make_request")

    telegram._send("a text")
    request_mock.assert_called_once_with(
        "POST",
        pytest.helpers.anyvar(str, strict=True),
        data={"chat_id": pytest.helpers.anyvar(str, strict=True), "text": "a text", "parse_mode": "HTML"})


def test_send_failed(telegram: Telegram, mocker: MockerFixture) -> None:
    """
    must reraise generic exception
    """
    mocker.patch("requests.Session.request", side_effect=Exception())
    with pytest.raises(Exception):
        telegram._send("a text")


def test_send_failed_http_error(telegram: Telegram, mocker: MockerFixture) -> None:
    """
    must reraise http exception
    """
    mocker.patch("requests.Session.request", side_effect=requests.HTTPError())
    with pytest.raises(requests.HTTPError):
        telegram._send("a text")


def test_generate(telegram: Telegram, package_ahriman: Package, result: Result,
                  mocker: MockerFixture) -> None:
    """
    must generate report
    """
    send_mock = mocker.patch("ahriman.core.report.telegram.Telegram._send")
    telegram.generate([package_ahriman], result)
    send_mock.assert_called_once_with(pytest.helpers.anyvar(int))


def test_generate_big_text_without_spaces(telegram: Telegram, package_ahriman: Package, result: Result,
                                          mocker: MockerFixture) -> None:
    """
    must raise ValueError in case if there are no new lines in text
    """
    mocker.patch("ahriman.core.report.jinja_template.JinjaTemplate.make_html", return_value="ab" * 4096)
    with pytest.raises(ValueError):
        telegram.generate([package_ahriman], result)


def test_generate_big_text(telegram: Telegram, package_ahriman: Package, result: Result,
                           mocker: MockerFixture) -> None:
    """
    must generate report with big text
    """
    mocker.patch("ahriman.core.report.jinja_template.JinjaTemplate.make_html", return_value="a\n" * 4096)
    send_mock = mocker.patch("ahriman.core.report.telegram.Telegram._send")

    telegram.generate([package_ahriman], result)
    send_mock.assert_has_calls([
        MockCall(pytest.helpers.anyvar(str, strict=True)), MockCall(pytest.helpers.anyvar(str, strict=True))
    ])


def test_generate_very_big_text(telegram: Telegram, package_ahriman: Package, result: Result,
                                mocker: MockerFixture) -> None:
    """
    must generate report with very big text
    """
    mocker.patch("ahriman.core.report.jinja_template.JinjaTemplate.make_html", return_value="ab\n" * 4096)
    send_mock = mocker.patch("ahriman.core.report.telegram.Telegram._send")

    telegram.generate([package_ahriman], result)
    send_mock.assert_has_calls([
        MockCall(pytest.helpers.anyvar(str, strict=True)),
        MockCall(pytest.helpers.anyvar(str, strict=True)),
        MockCall(pytest.helpers.anyvar(str, strict=True)),
    ])


def test_generate_no_empty(telegram: Telegram, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must generate report
    """
    send_mock = mocker.patch("ahriman.core.report.telegram.Telegram._send")
    telegram.generate([package_ahriman], Result())
    send_mock.assert_not_called()
