import pytest

from ahriman.core.triggers import Trigger
from ahriman.models.result import Result


def test_run(trigger: Trigger) -> None:
    """
    must raise NotImplemented for missing rum method
    """
    with pytest.raises(NotImplementedError):
        trigger.run(Result(), [])
