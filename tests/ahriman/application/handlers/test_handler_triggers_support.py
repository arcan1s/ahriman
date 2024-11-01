from ahriman.application.handlers.triggers import Triggers
from ahriman.application.handlers.triggers_support import TriggersSupport


def test_arguments() -> None:
    """
    must define own arguments
    """
    assert TriggersSupport.arguments != Triggers.arguments
