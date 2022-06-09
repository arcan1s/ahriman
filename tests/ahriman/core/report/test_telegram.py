import pytest
import requests

from pytest_mock import MockerFixture
from unittest import mock

from ahriman.core.configuration import Configuration
from ahriman.core.report import Telegram
from ahriman.models.package import Package
from ahriman.models.result import Result


def test_send(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must send a message
    """
    request_mock = mocker.patch("requests.post")
    report = Telegram("x86_64", configuration, "telegram")

    report._send("a text")
    request_mock.assert_called_once_with(
        pytest.helpers.anyvar(str, strict=True),
        data={"chat_id": pytest.helpers.anyvar(str, strict=True), "text": "a text", "parse_mode": "HTML"})


def test_send_failed(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must reraise generic exception
    """
    mocker.patch("requests.post", side_effect=Exception())
    report = Telegram("x86_64", configuration, "telegram")

    with pytest.raises(Exception):
        report._send("a text")


def test_make_request_failed_http_error(configuration: Configuration, mocker: MockerFixture) -> None:
    """
    must reraise http exception
    """
    mocker.patch("requests.post", side_effect=requests.exceptions.HTTPError())
    report = Telegram("x86_64", configuration, "telegram")

    with pytest.raises(requests.exceptions.HTTPError):
        report._send("a text")


def test_generate(configuration: Configuration, package_ahriman: Package, result: Result,
                  mocker: MockerFixture) -> None:
    """
    must generate report
    """
    send_mock = mocker.patch("ahriman.core.report.Telegram._send")

    report = Telegram("x86_64", configuration, "telegram")
    report.generate([package_ahriman], result)
    send_mock.assert_called_once_with(pytest.helpers.anyvar(int))


def test_generate_big_text_without_spaces(configuration: Configuration, package_ahriman: Package, result: Result,
                                          mocker: MockerFixture) -> None:
    """
    must raise ValueError in case if there are no new lines in text
    """
    mocker.patch("ahriman.core.report.JinjaTemplate.make_html", return_value="ab" * 4096)
    report = Telegram("x86_64", configuration, "telegram")

    with pytest.raises(ValueError):
        report.generate([package_ahriman], result)


def test_generate_big_text(configuration: Configuration, package_ahriman: Package, result: Result,
                           mocker: MockerFixture) -> None:
    """
    must generate report with big text
    """
    mocker.patch("ahriman.core.report.JinjaTemplate.make_html", return_value="a\n" * 4096)
    send_mock = mocker.patch("ahriman.core.report.Telegram._send")

    report = Telegram("x86_64", configuration, "telegram")
    report.generate([package_ahriman], result)
    send_mock.assert_has_calls([
        mock.call(pytest.helpers.anyvar(str, strict=True)), mock.call(pytest.helpers.anyvar(str, strict=True))
    ])


def test_generate_very_big_text(configuration: Configuration, package_ahriman: Package, result: Result,
                                mocker: MockerFixture) -> None:
    """
    must generate report with very big text
    """
    mocker.patch("ahriman.core.report.JinjaTemplate.make_html", return_value="ab\n" * 4096)
    send_mock = mocker.patch("ahriman.core.report.Telegram._send")

    report = Telegram("x86_64", configuration, "telegram")
    report.generate([package_ahriman], result)
    send_mock.assert_has_calls([
        mock.call(pytest.helpers.anyvar(str, strict=True)),
        mock.call(pytest.helpers.anyvar(str, strict=True)),
        mock.call(pytest.helpers.anyvar(str, strict=True)),
    ])


def test_generate_no_empty(configuration: Configuration, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must generate report
    """
    send_mock = mocker.patch("ahriman.core.report.Telegram._send")

    report = Telegram("x86_64", configuration, "telegram")
    report.generate([package_ahriman], Result())
    send_mock.assert_not_called()
