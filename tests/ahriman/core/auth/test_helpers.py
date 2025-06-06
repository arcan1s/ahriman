import importlib
import sys

from pytest_mock import MockerFixture

from ahriman.core.auth import helpers


def test_import_aiohttp_security() -> None:
    """
    must import aiohttp_security correctly
    """
    assert helpers.aiohttp_security


async def test_authorized_userid_dummy(mocker: MockerFixture) -> None:
    """
    must not call authorized_userid from library if not enabled
    """
    mocker.patch.object(helpers, "aiohttp_security", None)
    await helpers.authorized_userid()


async def test_authorized_userid_library(mocker: MockerFixture) -> None:
    """
    must call authorized_userid from library if enabled
    """
    authorized_userid_mock = mocker.patch("aiohttp_security.authorized_userid")
    await helpers.authorized_userid()
    authorized_userid_mock.assert_called_once_with()


async def test_check_authorized_dummy(mocker: MockerFixture) -> None:
    """
    must not call check_authorized from library if not enabled
    """
    mocker.patch.object(helpers, "aiohttp_security", None)
    await helpers.check_authorized()


async def test_check_authorized_library(mocker: MockerFixture) -> None:
    """
    must call check_authorized from library if enabled
    """
    check_authorized_mock = mocker.patch("aiohttp_security.check_authorized")
    await helpers.check_authorized()
    check_authorized_mock.assert_called_once_with()


async def test_forget_dummy(mocker: MockerFixture) -> None:
    """
    must not call forget from library if not enabled
    """
    mocker.patch.object(helpers, "aiohttp_security", None)
    await helpers.forget()


async def test_forget_library(mocker: MockerFixture) -> None:
    """
    must call forget from library if enabled
    """
    forget_mock = mocker.patch("aiohttp_security.forget")
    await helpers.forget()
    forget_mock.assert_called_once_with()


async def test_remember_dummy(mocker: MockerFixture) -> None:
    """
    must not call remember from library if not enabled
    """
    mocker.patch.object(helpers, "aiohttp_security", None)
    await helpers.remember()


async def test_remember_library(mocker: MockerFixture) -> None:
    """
    must call remember from library if enabled
    """
    remember_mock = mocker.patch("aiohttp_security.remember")
    await helpers.remember()
    remember_mock.assert_called_once_with()


def test_import_aiohttp_security_missing(mocker: MockerFixture) -> None:
    """
    must set missing flag if no aiohttp_security module found
    """
    mocker.patch.dict(sys.modules, {"aiohttp_security": None})
    importlib.reload(helpers)
    assert helpers.aiohttp_security is None
