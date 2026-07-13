#
# Copyright (c) 2021-2026 ahriman team.
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
from typing import ClassVar

from ahriman.core.configuration import Configuration


class StatusViewGuard:
    """
    helper for check if status routes are enabled
    """

    ROUTES: ClassVar[list[str]]

    @classmethod
    def routes(cls, configuration: Configuration) -> list[str]:
        """
        extract routes list for the view

        Args:
            configuration(Configuration): configuration instance

        Returns:
            list[str]: list of routes defined for the view. By default, it tries to read :attr:`ROUTES` option if set
            and returns empty list otherwise
        """
        if configuration.getboolean("web", "service_only", fallback=False):
            return []
        return cls.ROUTES
