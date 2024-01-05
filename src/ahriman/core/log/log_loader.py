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
import logging

from logging.config import fileConfig
from pathlib import Path

from ahriman.core.configuration import Configuration
from ahriman.core.log.http_log_handler import HttpLogHandler
from ahriman.models.log_handler import LogHandler
from ahriman.models.repository_id import RepositoryId


class LogLoader:
    """
    simple static method class which setups application loggers

    Attributes:
        DEFAULT_LOG_FORMAT(str): (class attribute) default log format (in case of fallback)
        DEFAULT_LOG_LEVEL(int): (class attribute) default log level (in case of fallback)
        DEFAULT_SYSLOG_DEVICE(Path): (class attribute) default path to syslog device
    """

    DEFAULT_LOG_FORMAT = "[%(levelname)s %(asctime)s] [%(filename)s:%(lineno)d %(funcName)s]: %(message)s"
    DEFAULT_LOG_LEVEL = logging.DEBUG
    DEFAULT_SYSLOG_DEVICE = Path("/") / "dev" / "log"

    @staticmethod
    def handler(selected: LogHandler | None) -> LogHandler:
        """
        try to guess default log handler. In case if ``selected`` is set, it will return specified value with appended
        _handler suffix. Otherwise, it will try to import journald handler and returns
        :attr:`ahriman.models.log_handler.LogHandler.Journald` if library is available. Otherwise, it will check if
        there is ``/dev/log`` device and returns :attr:`ahriman.models.log_handler.LogHandler.Syslog` in this
        case. And, finally, it will fall back to :attr:`ahriman.models.log_handler.LogHandler.Console`
        if none were found

        Args:
            selected(LogHandler | None): user specified handler if any

        Returns:
            LogHandler: selected log handler
        """
        if selected is not None:
            return selected

        try:
            from systemd.journal import JournalHandler  # type: ignore[import-untyped]
            del JournalHandler
            return LogHandler.Journald  # journald import was found
        except ImportError:
            if LogLoader.DEFAULT_SYSLOG_DEVICE.exists():
                return LogHandler.Syslog
            return LogHandler.Console

    @staticmethod
    def load(repository_id: RepositoryId, configuration: Configuration, handler: LogHandler, *,
             quiet: bool, report: bool) -> None:
        """
        setup logging settings from configuration

        Args:
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
            handler(LogHandler): selected default log handler, which will be used if no handlers were set
            quiet(bool): force disable any log messages
            report(bool): force enable or disable reporting
        """
        default_handler = f"{handler.value}_handler"

        try:
            log_configuration = Configuration()
            log_configuration.read(configuration.logging_path)

            # set handlers if they are not set
            for section in filter(lambda s: s.startswith("logger_"), log_configuration.sections()):
                if "handlers" in log_configuration[section]:
                    continue
                log_configuration.set_option(section, "handlers", default_handler)

            # load logging configuration
            fileConfig(log_configuration, disable_existing_loggers=True)
            logging.debug("using %s logger", default_handler)
        except Exception:
            logging.basicConfig(filename=None, format=LogLoader.DEFAULT_LOG_FORMAT, level=LogLoader.DEFAULT_LOG_LEVEL)
            logging.exception("could not load logging from configuration, fallback to stderr")

        HttpLogHandler.load(repository_id, configuration, report=report)

        if quiet:
            logging.disable(logging.WARNING)  # only print errors here
