from ahriman.core.formatters.user_printer import UserPrinter


def test_properties(user_printer: UserPrinter) -> None:
    """
    must return non empty properties list
    """
    assert user_printer.properties()


def test_title(user_printer: UserPrinter) -> None:
    """
    must return non empty title
    """
    assert user_printer.title() is not None
