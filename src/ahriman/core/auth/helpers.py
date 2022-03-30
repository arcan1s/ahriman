#
# Copyright (c) 2021-2022 ahriman team.
#
# This file is part of ahriman
# (see https://github.com/arcan1s/ahriman).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
from typing import Any

try:
    import aiohttp_security  # type: ignore
    _has_aiohttp_security = True
except ImportError:
    _has_aiohttp_security = False


async def authorized_userid(*args: Any) -> Any:
    """
    handle aiohttp security methods
    :param args: argument list as provided by authorized_userid function
    :return: None in case if no aiohttp_security module found and function call otherwise
    """
    if _has_aiohttp_security:
        return await aiohttp_security.authorized_userid(*args)  # pylint: disable=no-value-for-parameter
    return None


async def check_authorized(*args: Any) -> Any:
    """
    handle aiohttp security methods
    :param args: argument list as provided by check_authorized function
    :return: None in case if no aiohttp_security module found and function call otherwise
    """
    if _has_aiohttp_security:
        return await aiohttp_security.check_authorized(*args)  # pylint: disable=no-value-for-parameter
    return None


async def forget(*args: Any) -> Any:
    """
    handle aiohttp security methods
    :param args: argument list as provided by forget function
    :return: None in case if no aiohttp_security module found and function call otherwise
    """
    if _has_aiohttp_security:
        return await aiohttp_security.forget(*args)  # pylint: disable=no-value-for-parameter
    return None


async def remember(*args: Any) -> Any:
    """
    handle disabled auth
    :param args: argument list as provided by remember function
    :return: None in case if no aiohttp_security module found and function call otherwise
    """
    if _has_aiohttp_security:
        return await aiohttp_security.remember(*args)  # pylint: disable=no-value-for-parameter
    return None
