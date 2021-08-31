import importlib
import sys

import ahriman.core.auth.helpers as helpers

from pytest_mock import MockerFixture


def test_import_aiohttp_security() -> None:
    """
    must import aiohttp_security correctly
    """
    assert helpers._has_aiohttp_security


def test_import_aiohttp_security_missing(mocker: MockerFixture) -> None:
    """
    must set missing flag if no aiohttp_security module found
    """
    mocker.patch.dict(sys.modules, {"aiohttp_security": None})
    importlib.reload(helpers)
    assert not helpers._has_aiohttp_security


async def test_authorized_userid_dummy(mocker: MockerFixture) -> None:
    """
    must not call authorized_userid from library if not enabled
    """
    mocker.patch.object(helpers, "_has_aiohttp_security", False)
    authorized_userid_mock = mocker.patch("aiohttp_security.authorized_userid")
    await helpers.authorized_userid()
    authorized_userid_mock.assert_not_called()


async def test_authorized_userid_library(mocker: MockerFixture) -> None:
    """
    must call authorized_userid from library if enabled
    """
    mocker.patch.object(helpers, "_has_aiohttp_security", True)
    authorized_userid_mock = mocker.patch("aiohttp_security.authorized_userid")
    await helpers.authorized_userid()
    authorized_userid_mock.assert_called_once()


async def test_check_authorized_dummy(mocker: MockerFixture) -> None:
    """
    must not call check_authorized from library if not enabled
    """
    mocker.patch.object(helpers, "_has_aiohttp_security", False)
    check_authorized_mock = mocker.patch("aiohttp_security.check_authorized")
    await helpers.check_authorized()
    check_authorized_mock.assert_not_called()


async def test_check_authorized_library(mocker: MockerFixture) -> None:
    """
    must call check_authorized from library if enabled
    """
    mocker.patch.object(helpers, "_has_aiohttp_security", True)
    check_authorized_mock = mocker.patch("aiohttp_security.check_authorized")
    await helpers.check_authorized()
    check_authorized_mock.assert_called_once()


async def test_forget_dummy(mocker: MockerFixture) -> None:
    """
    must not call forget from library if not enabled
    """
    mocker.patch.object(helpers, "_has_aiohttp_security", False)
    forget_mock = mocker.patch("aiohttp_security.forget")
    await helpers.forget()
    forget_mock.assert_not_called()


async def test_forget_library(mocker: MockerFixture) -> None:
    """
    must call forget from library if enabled
    """
    mocker.patch.object(helpers, "_has_aiohttp_security", True)
    forget_mock = mocker.patch("aiohttp_security.forget")
    await helpers.forget()
    forget_mock.assert_called_once()


async def test_remember_dummy(mocker: MockerFixture) -> None:
    """
    must not call remember from library if not enabled
    """
    mocker.patch.object(helpers, "_has_aiohttp_security", False)
    remember_mock = mocker.patch("aiohttp_security.remember")
    await helpers.remember()
    remember_mock.assert_not_called()


async def test_remember_library(mocker: MockerFixture) -> None:
    """
    must call remember from library if enabled
    """
    mocker.patch.object(helpers, "_has_aiohttp_security", True)
    remember_mock = mocker.patch("aiohttp_security.remember")
    await helpers.remember()
    remember_mock.assert_called_once()
