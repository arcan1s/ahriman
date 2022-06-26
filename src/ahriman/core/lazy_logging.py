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

from typing import Any


class LazyLogging:
    """
    wrapper for the logger library inspired by scala lazy logging module

    Attributes:
        logger(logging.Logger): class logger instance
    """

    logger: logging.Logger

    def __getattr__(self, item: str) -> Any:
        """
        logger extractor

        Args:
            item(str) property name:

        Returns:
            Any: attribute by its name

        Raises:
            AttributeError: in case if no such attribute found
        """
        if item == "logger":
            logger = logging.getLogger(self.logger_name)
            setattr(self, item, logger)
            return logger
        raise AttributeError(f"'{self.__class__.__qualname__}' object has no attribute '{item}'")

    @property
    def logger_name(self) -> str:
        """
        extract logger name for the class

        Returns:
            str: logger name as combination of module name and class name
        """
        clazz = self.__class__
        prefix = "" if clazz.__module__ is None else f"{clazz.__module__}."
        return f"{prefix}{self.__class__.__qualname__}"
