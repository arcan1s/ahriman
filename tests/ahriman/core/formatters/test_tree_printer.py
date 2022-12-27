from ahriman.core.formatters import TreePrinter


def test_properties(tree_printer: TreePrinter) -> None:
    """
    must return non-empty properties list
    """
    assert tree_printer.properties()


def test_title(tree_printer: TreePrinter) -> None:
    """
    must return non-empty title
    """
    assert tree_printer.title() is not None
