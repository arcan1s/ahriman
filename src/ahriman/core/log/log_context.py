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
import contextvars
import logging

from typing import Any, ClassVar, TypeVar, cast


T = TypeVar("T")


class LogContext:
    """
    logging context manager which provides context variables injection into log records
    """

    _context: ClassVar[dict[str, contextvars.ContextVar[Any]]] = {}

    @classmethod
    def get(cls, name: str) -> T | None:
        """
        get context variable if available

        Args:
            name(str): name of the context variable

        Returns:
            T | None: context variable if available and ``None`` otherwise
        """
        if (variable := cls._context.get(name)) is not None:
            return cast(T | None, variable.get())
        return None

    @classmethod
    def log_record_factory(cls, *args: Any, **kwargs: Any) -> logging.LogRecord:
        """
        log record factory which injects all registered context variables into log records

        Args:
            *args(Any): positional arguments for the log factory
            **kwargs(Any): keyword arguments for the log factory

        Returns:
            logging.LogRecord: log record with context variables set as attributes
        """
        record = logging.LogRecord(*args, **kwargs)

        for name, variable in cls._context.items():
            if (value := variable.get()) is not None:
                setattr(record, name, value)

        return record

    @classmethod
    def register(cls, name: str) -> contextvars.ContextVar[T]:
        """
        (re)create context variable for log records

        Args:
            name(str): name of the context variable

        Returns:
            contextvars.ContextVar[T]: created context variable
        """
        variable = cls._context[name] = contextvars.ContextVar(name, default=None)
        return variable

    @classmethod
    def reset(cls, name: str, token: contextvars.Token[T]) -> None:
        """
        reset context variable to its previous value

        Args:
            name(str): attribute name to reset on log records
            token(contextvars.Token[T]): previously registered token
        """
        cls._context[name].reset(token)

    @classmethod
    def set(cls, name: str, value: T) -> contextvars.Token[T]:
        """
        set context variable for log records. This value will be automatically emitted with each log record

        Args:
            name(str): attribute name to set on log records
            value(T): current value of the context variable

        Returns:
            contextvars.Token[T]: token created with this value
        """
        return cls._context[name].set(value)
