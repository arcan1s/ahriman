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
import contextlib
import logging

from collections.abc import Iterator
from functools import cached_property
from typing import Any

from ahriman.core.log.log_context import LogContext
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

    @contextlib.contextmanager
    def in_context(self, name: str, value: Any) -> Iterator[None]:
        """
        execute function while setting log context. The context will be reset after the execution

        Args:
            name(str): attribute name to set on log records
            value(Any): current value of the context variable
        """
        token = LogContext.set(name, value)
        try:
            yield
        finally:
            LogContext.reset(name, token)

    @contextlib.contextmanager
    def in_package_context(self, package_base: str, version: str | None) -> Iterator[None]:
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
        with self.in_context("package_id", LogRecordId(package_base, version or "<unknown>")):
            yield
