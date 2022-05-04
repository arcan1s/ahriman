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
import logging
import sqlite3

from pathlib import Path
from sqlite3 import Connection, Cursor
from typing import Any, Dict, Tuple, TypeVar, Callable


T = TypeVar("T")


class Operations:
    """
    base operation class

    Attributes:
        logger(logging.Logger): class logger
        path(Path): path to the database file
    """

    def __init__(self, path: Path) -> None:
        """
        default constructor

        Args:
            path(Path): path to the database file
        """
        self.path = path
        self.logger = logging.getLogger("database")

    @staticmethod
    def factory(cursor: Cursor, row: Tuple[Any, ...]) -> Dict[str, Any]:
        """
        dictionary factory based on official documentation

        Args:
            cursor(Cursor): cursor descriptor
            row(Tuple[Any, ...]): fetched row

        Returns:
            Dict[str, Any]: row converted to dictionary
        """
        result = {}
        for index, column in enumerate(cursor.description):
            result[column[0]] = row[index]
        return result

    def with_connection(self, query: Callable[[Connection], T], commit: bool = False) -> T:
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
