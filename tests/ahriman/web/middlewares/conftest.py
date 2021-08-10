import pytest

from collections import namedtuple


_request = namedtuple("_request", ["path"])


@pytest.fixture
def aiohttp_request() -> _request:
    """
    fixture for aiohttp like object
    :return: aiohttp like request test instance
    """
    return _request("path")
