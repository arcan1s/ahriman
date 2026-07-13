from pathlib import Path

import pytest

from fixtures import *  # pylint: disable=wildcard-import,unused-wildcard-import


@pytest.fixture
def resource_path_root() -> Path:
    return Path(__file__).resolve().parents[2] / "tests" / "testresources"
