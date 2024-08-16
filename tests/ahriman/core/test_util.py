import ahriman.core.utils

from ahriman.core.util import *


def test_import() -> None:
    """
    ahriman.core.util must provide same methods as ahriman.core.utils module
    """
    for method in dir():
        assert hasattr(ahriman.core.utils, method)
