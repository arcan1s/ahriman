#
# Copyright (c) 2021-2024 ahriman team.
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
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse

from ahriman.core.util import dataclass_view


@dataclass(frozen=True)
class Worker:
    """
    worker descriptor

    Attributes:
        address(str): worker address to be reachable outside
        identifier(str): worker unique identifier. If none set it will be automatically generated from the address
    """

    address: str
    identifier: str = field(default="", kw_only=True)

    def __post_init__(self) -> None:
        """
        update identifier based on settings
        """
        object.__setattr__(self, "identifier", self.identifier or urlparse(self.address).netloc)

    def view(self) -> dict[str, Any]:
        """
        generate json patch view

        Returns:
            dict[str, Any]: json-friendly dictionary
        """
        return dataclass_view(self)
