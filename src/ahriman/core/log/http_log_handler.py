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
import logging
import uuid

from typing import Self

from ahriman.core.configuration import Configuration
from ahriman.core.status import Client
from ahriman.models.log_record import LogRecord
from ahriman.models.log_record_id import LogRecordId
from ahriman.models.repository_id import RepositoryId


class HttpLogHandler(logging.Handler):
    """
    handler for the http logging. Because default :class:`logging.handlers.HTTPHandler` does not support cookies
    authorization, we have to implement own handler which overrides the :func:`logging.handlers.HTTPHandler.emit()`
    method

    Attributes:
        reporter(Client): build status reporter instance
        suppress_errors(bool): suppress logging errors (e.g. if no web server available)
    """

    def __init__(self, repository_id: RepositoryId, configuration: Configuration, *,
                 report: bool, suppress_errors: bool) -> None:
        """
        Args:
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
            report(bool): force enable or disable reporting
            suppress_errors(bool): suppress logging errors (e.g. if no web server available)
        """
        # we don't really care about those parameters because they will be handled by the reporter
        logging.Handler.__init__(self)

        self.reporter = Client.load(repository_id, configuration, report=report)
        self.suppress_errors = suppress_errors

    @classmethod
    def load(cls, repository_id: RepositoryId, configuration: Configuration, *, report: bool) -> Self:
        """
        install logger. This function creates handler instance and adds it to the handler list in case if no other
        http handler found

        Args:
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
            report(bool): force enable or disable reporting

        Returns:
            Self: logger instance with loaded settings
        """
        root = logging.getLogger()
        if (handler := next((handler for handler in root.handlers if isinstance(handler, cls)), None)) is not None:
            return handler  # there is already registered instance

        suppress_errors = configuration.getboolean(  # read old-style first and then fallback to new style
            "settings", "suppress_http_log_errors",
            fallback=configuration.getboolean("status", "suppress_http_log_errors", fallback=False))
        handler = cls(repository_id, configuration, report=report, suppress_errors=suppress_errors)
        root.addHandler(handler)

        LogRecordId.DEFAULT_PROCESS_ID = str(uuid.uuid4())  # assign default process identifier for log records

        return handler

    def emit(self, record: logging.LogRecord) -> None:
        """
        emit log records using reporter client

        Args:
            record(logging.LogRecord): log record to log
        """
        log_record_id = getattr(record, "package_id", None)
        if log_record_id is None:
            return  # in case if no package base supplied we need just skip log message

        try:
            self.reporter.package_logs_add(LogRecord(log_record_id, record.created, record.getMessage()))
        except Exception:
            if self.suppress_errors:
                return
            self.handleError(record)
