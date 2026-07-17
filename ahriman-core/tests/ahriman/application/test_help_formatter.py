from ahriman.application.help_formatter import _HelpFormatter


def test_whitespace_matcher(formatter: _HelpFormatter) -> None:
    """
    must only match spaces or tabs
    """
    assert formatter._whitespace_matcher.match(" ")
    assert formatter._whitespace_matcher.match("\t")

    assert formatter._whitespace_matcher.match("\n") is None
    assert formatter._whitespace_matcher.match("\r") is None


def test_fill_text(formatter: _HelpFormatter) -> None:
    """
    must wrap text keeping new lines
    """
    assert formatter._fill_text("first\n 1    longwordhere", 10, "") == "first\n 1 longwor\ndhere"
