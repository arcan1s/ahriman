# pylint: disable=wildcard-import,unused-wildcard-import
from fixtures import *
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests"))


@pytest.fixture
def resource_path_root() -> Path:
    return Path(__file__).resolve().parents[2] / "tests" / "testresources"
