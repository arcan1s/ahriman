import pytest

from email.utils import parsedate_to_datetime
from pytest_mock import MockerFixture
from unittest.mock import MagicMock

from ahriman.core.report.rss import RSS
from ahriman.core.status import Client
from ahriman.core.utils import utcnow
from ahriman.models.event import Event, EventType
from ahriman.models.package import Package
from ahriman.models.result import Result


def test_format_datetime() -> None:
    """
    must format timestamp to rfc format
    """
    timestamp = utcnow().replace(microsecond=0)
    assert parsedate_to_datetime(RSS.format_datetime(timestamp.timestamp())) == timestamp


def test_format_datetime_datetime() -> None:
    """
    must format datetime to rfc format
    """
    timestamp = utcnow().replace(microsecond=0)
    assert parsedate_to_datetime(RSS.format_datetime(timestamp)) == timestamp


def test_format_datetime_empty() -> None:
    """
    must generate empty string from None timestamp
    """
    assert RSS.format_datetime(None) == ""


def test_sort_content() -> None:
    """
    must sort content for the template
    """
    assert RSS.sort_content([
        {"filename": "2", "build_date": "Thu, 29 Aug 2024 16:36:55 -0000"},
        {"filename": "1", "build_date": "Thu, 29 Aug 2024 16:36:54 -0000"},
        {"filename": "3", "build_date": "Thu, 29 Aug 2024 16:36:56 -0000"},
    ]) == [
        {"filename": "3", "build_date": "Thu, 29 Aug 2024 16:36:56 -0000"},
        {"filename": "2", "build_date": "Thu, 29 Aug 2024 16:36:55 -0000"},
        {"filename": "1", "build_date": "Thu, 29 Aug 2024 16:36:54 -0000"},
    ]


def test_content(rss: RSS, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must generate RSS content correctly
    """
    client_mock = MagicMock()
    client_mock.event_get.return_value = [
        Event(EventType.PackageUpdated, package_ahriman.base),
        Event(EventType.PackageUpdated, "random"),
        Event(EventType.PackageUpdated, package_ahriman.base),
    ]
    context_mock = mocker.patch("ahriman.core._Context.get", return_value=client_mock)

    assert rss.content([package_ahriman]).success == [package_ahriman]
    context_mock.assert_called_once_with(Client)
    client_mock.event_get.assert_called_once_with(EventType.PackageUpdated, None, limit=rss.max_entries)


def test_generate(rss: RSS, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must generate report
    """
    content_mock = mocker.patch("ahriman.core.report.rss.RSS.content", return_value=Result())
    write_mock = mocker.patch("pathlib.Path.write_text")

    rss.generate([package_ahriman], Result())
    content_mock.assert_called_once_with([package_ahriman])
    write_mock.assert_called_once_with(pytest.helpers.anyvar(int), encoding="utf8")
