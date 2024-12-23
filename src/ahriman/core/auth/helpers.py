#
# Copyright (c) 2021-2025 ahriman team.
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
try:
    import aiohttp_security
except ImportError:
    aiohttp_security = None  # type: ignore[assignment]

from typing import Any


__all__ = ["authorized_userid", "check_authorized", "forget", "remember"]


async def authorized_userid(*args: Any, **kwargs: Any) -> Any:
    """
    handle aiohttp security methods

    Args:
        *args(Any): argument list as provided by authorized_userid function
        **kwargs(Any): named argument list as provided by authorized_userid function

    Returns:
        Any: ``None`` in case if no aiohttp_security module found and function call otherwise
    """
    if aiohttp_security is not None:
        return await aiohttp_security.authorized_userid(*args, **kwargs)  # pylint: disable=no-value-for-parameter
    return None


async def check_authorized(*args: Any, **kwargs: Any) -> Any:
    """
    handle aiohttp security methods

    Args:
        *args(Any): argument list as provided by check_authorized function
        **kwargs(Any): named argument list as provided by authorized_userid function

    Returns:
        Any: ``None`` in case if no aiohttp_security module found and function call otherwise
    """
    if aiohttp_security is not None:
        return await aiohttp_security.check_authorized(*args, **kwargs)  # pylint: disable=no-value-for-parameter
    return None


async def forget(*args: Any, **kwargs: Any) -> Any:
    """
    handle aiohttp security methods

    Args:
        *args(Any): argument list as provided by forget function
        **kwargs(Any): named argument list as provided by authorized_userid function

    Returns:
        Any: ``None`` in case if no aiohttp_security module found and function call otherwise
    """
    if aiohttp_security is not None:
        return await aiohttp_security.forget(*args, **kwargs)  # pylint: disable=no-value-for-parameter
    return None


async def remember(*args: Any, **kwargs: Any) -> Any:
    """
    handle disabled auth

    Args:
        *args(Any): argument list as provided by remember function
        **kwargs(Any): named argument list as provided by authorized_userid function

    Returns:
        Any: ``None`` in case if no aiohttp_security module found and function call otherwise
    """
    if aiohttp_security is not None:
        return await aiohttp_security.remember(*args, **kwargs)  # pylint: disable=no-value-for-parameter
    return None
