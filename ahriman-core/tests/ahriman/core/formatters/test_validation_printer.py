from ahriman.core.formatters import ValidationPrinter
from ahriman.models.property import Property


def test_properties(validation_printer: ValidationPrinter) -> None:
    """
    must return non-empty properties list
    """
    assert validation_printer.properties()


def test_title(validation_printer: ValidationPrinter) -> None:
    """
    must return non-empty title
    """
    assert validation_printer.title() is not None


def test_get_error_messages(validation_printer: ValidationPrinter) -> None:
    """
    must get error messages from plain list
    """
    result = ValidationPrinter.get_error_messages(validation_printer.node, validation_printer.errors)
    assert list(result) == [
        Property("root", "root error", is_required=True, indent=1),
        Property("child", "child error", is_required=True, indent=2),
        Property("grandchild", "grandchild error", is_required=True, indent=3),
    ]
