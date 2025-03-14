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
import contextlib
import logging

from collections.abc import Generator
from functools import cached_property
from typing import Any

from ahriman.models.log_record_id import LogRecordId


class LazyLogging:
    """
    wrapper for the logger library inspired by scala lazy logging module
    """

    @cached_property
    def logger(self) -> logging.Logger:
        """
        get class logger instance

        Returns:
            logging.Logger: class logger instance
        """
        return logging.getLogger(self.logger_name)

    @property
    def logger_name(self) -> str:
        """
        extract logger name for the class

        Returns:
            str: logger name as combination of module name and class name
        """
        clazz = self.__class__
        prefix = "" if clazz.__module__ is None else f"{clazz.__module__}."
        return f"{prefix}{clazz.__qualname__}"

    @staticmethod
    def _package_logger_reset() -> None:
        """
        reset package logger to empty one
        """
        logging.setLogRecordFactory(logging.LogRecord)

    @staticmethod
    def _package_logger_set(package_base: str, version: str | None) -> None:
        """
        set package base as extra info to the logger

        Args:
            package_base(str): package base
            version(str | None): package version if available
        """
        current_factory = logging.getLogRecordFactory()

        def package_record_factory(*args: Any, **kwargs: Any) -> logging.LogRecord:
            record = current_factory(*args, **kwargs)
            record.package_id = LogRecordId(package_base, version or "<unknown>")
            return record

        logging.setLogRecordFactory(package_record_factory)

    @contextlib.contextmanager
    def in_package_context(self, package_base: str, version: str | None) -> Generator[None, None, None]:
        """
        execute function while setting package context

        Args:
            package_base(str): package base to set context in
            version(str | None): package version if available

        Examples:
            This function is designed to be called as context manager with ``package_base`` argument, e.g.:

                >>> with self.in_package_context(package.base, package.version):
                >>>     build_package(package)
        """
        try:
            self._package_logger_set(package_base, version)
            yield
        finally:
            self._package_logger_reset()
