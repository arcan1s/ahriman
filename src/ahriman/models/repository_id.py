#
# Copyright (c) 2021-2023 ahriman team.
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
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RepositoryId:
    """
    unique identifier of the repository

    Attributes:
        architecture(str): repository architecture
        name(str): repository name
    """

    architecture: str
    name: str

    @property
    def is_empty(self) -> bool:
        """
        check if all data is supplied for the loading

        Returns:
            bool: True in case if architecture or name are not set and False otherwise
        """
        return not self.architecture or not self.name

    @property
    def id(self) -> str:
        """
        get repository id to be used for databases

        Returns:
            str: unique id for this repository
        """
        if self.is_empty:
            return ""
        return f"{self.architecture}-{self.name}"  # basically the same as used for command line

    def query(self) -> list[tuple[str, str]]:
        """
        generate query parameters

        Returns:
            list[tuple[str, str]]: json view as query parameters
        """
        return list(self.view().items())

    def view(self) -> dict[str, Any]:
        """
        generate json package view

        Returns:
            dict[str, Any]: json-friendly dictionary
        """
        return {
            "architecture": self.architecture,
            "repository": self.name,
        }

    def __lt__(self, other: Any) -> bool:
        """
        comparison operator for sorting

        Args:
            other(Any): other object to compare

        Returns:
            bool: True in case if this is less than other and False otherwise

        Raises:
            TypeError: if other is different from RepositoryId type
        """
        if not isinstance(other, RepositoryId):
            raise ValueError(f"'<' not supported between instances of '{type(self)}' and '{type(other)}'")

        return (self.name, self.architecture) < (other.name, other.architecture)
