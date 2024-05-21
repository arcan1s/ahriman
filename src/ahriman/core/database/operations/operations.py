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
import sqlite3

from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

from ahriman.core.log import LazyLogging
from ahriman.models.repository_id import RepositoryId
from ahriman.models.repository_paths import RepositoryPaths


T = TypeVar("T")


class Operations(LazyLogging):
    """
    base operation class

    Attributes:
        path(Path): path to the database file
    """

    def __init__(self, path: Path, repository_id: RepositoryId, repository_paths: RepositoryPaths) -> None:
        """
        default constructor

        Args:
            path(Path): path to the database file
            repository_id(RepositoryId): repository unique identifier
        """
        self.path = path
        self._repository_id = repository_id
        self._repository_paths = repository_paths

    @staticmethod
    def factory(cursor: sqlite3.Cursor, row: tuple[Any, ...]) -> dict[str, Any]:
        """
        dictionary factory based on official documentation

        Args:
            cursor(Cursor): cursor descriptor
            row(tuple[Any, ...]): fetched row

        Returns:
            dict[str, Any]: row converted to dictionary
        """
        result = {}
        for index, column in enumerate(cursor.description):
            result[column[0]] = row[index]
        return result

    def with_connection(self, query: Callable[[sqlite3.Connection], T], *, commit: bool = False) -> T:
        """
        perform operation in connection

        Args:
            query(Callable[[Connection], T]): function to be called with connection
            commit(bool, optional): if True commit() will be called on success (Default value = False)

        Returns:
            T: result of the ``query`` call
        """
        with sqlite3.connect(self.path, detect_types=sqlite3.PARSE_DECLTYPES) as connection:
            connection.row_factory = self.factory
            result = query(connection)
            if commit:
                connection.commit()
        return result
