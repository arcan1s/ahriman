from ahriman.core.formatters import PatchPrinter


def test_properties(patch_printer: PatchPrinter) -> None:
    """
    must return non empty properties list
    """
    assert patch_printer.properties()


def test_properties_required(patch_printer: PatchPrinter) -> None:
    """
    must return all properties as required
    """
    assert all(prop.is_required for prop in patch_printer.properties())


def test_title(patch_printer: PatchPrinter) -> None:
    """
    must return non empty title
    """
    assert patch_printer.title() == "ahriman"
