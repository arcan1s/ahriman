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
# pylint: disable=imports-out-of-order
from logging import NullHandler
from typing import Any


__all__ = ["JournalHandler"]


class _JournalHandler(NullHandler):
    """
    wrapper for unexpected args and kwargs
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Args:
            *args(Any): positional arguments
            **kwargs(Any): keyword arguments
        """
        NullHandler.__init__(self)
        del args, kwargs


try:
    from systemd.journal import JournalHandler  # type: ignore[import-untyped]
except ImportError:
    JournalHandler = _JournalHandler
