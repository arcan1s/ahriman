import sys

from pytest_mock import MockerFixture


# because of how imports work it must be first test
def test_dummy_journal_handler(mocker: MockerFixture) -> None:
    """
    must import dummy journal handler if upstream systemd was not found
    """
    mocker.patch.dict(sys.modules, {"systemd.journal": None})
    from logging import NullHandler
    from ahriman.core.log.journal_handler import JournalHandler
    assert issubclass(JournalHandler, NullHandler)


def test_init() -> None:
    """
    must init dummy handler
    """
    from ahriman.core.log.journal_handler import _JournalHandler
    assert _JournalHandler(42, answer=42)


def test_journal_handler() -> None:
    """
    must import journal handler
    """
    from systemd.journal import JournalHandler as UpstreamJournalHandler
    from ahriman.core.log.journal_handler import JournalHandler
    assert JournalHandler is UpstreamJournalHandler
