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
from __future__ import annotations

import logging

from ahriman.core.configuration import Configuration


class HttpLogHandler(logging.Handler):
    """
    handler for the http logging. Because default ``logging.handlers.HTTPHandler`` does not support cookies
    authorization, we have to implement own handler which overrides the ``logging.handlers.HTTPHandler.emit`` method

    Attributes:
        reporter(Client): build status reporter instance
    """

    def __init__(self, configuration: Configuration, *, report: bool) -> None:
        """
        default constructor

        Args:
            configuration(Configuration): configuration instance
            report(bool): force enable or disable reporting
        """
        # we don't really care about those parameters because they will be handled by the reporter
        logging.Handler.__init__(self)

        # client has to be importer here because of circular imports
        from ahriman.core.status.client import Client
        self.reporter = Client.load(configuration, report=report)

    @classmethod
    def load(cls, configuration: Configuration, *, report: bool) -> HttpLogHandler:
        """
        install logger. This function creates handler instance and adds it to the handler list in case if no other
        http handler found

        Args:
            configuration(Configuration): configuration instance
            report(bool): force enable or disable reporting
        """
        root = logging.getLogger()
        if (handler := next((handler for handler in root.handlers if isinstance(handler, cls)), None)) is not None:
            return handler  # there is already registered instance

        handler = cls(configuration, report=report)
        root.addHandler(handler)

        return handler

    def emit(self, record: logging.LogRecord) -> None:
        """
        emit log records using reporter client

        Args:
            record(logging.LogRecord): log record to log
        """
        try:
            self.reporter.logs(record)
        except Exception:
            self.handleError(record)
