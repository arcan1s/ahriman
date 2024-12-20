import importlib
import sys

from pytest_mock import MockerFixture
from ahriman.web import apispec


def test_import_apispec() -> None:
    """
    must correctly import apispec
    """
    assert apispec.aiohttp_apispec


def test_import_apispec_missing(mocker: MockerFixture) -> None:
    """
    must correctly process missing module
    """
    mocker.patch.dict(sys.modules, {"aiohttp_apispec": None})
    importlib.reload(apispec)

    assert apispec.aiohttp_apispec is None
    assert apispec.Schema
    assert apispec.fields("arg", kwargs=42)
