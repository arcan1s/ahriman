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
import logging

from logging.config import fileConfig

from ahriman.core.configuration import Configuration
from ahriman.core.log.http_log_handler import HttpLogHandler


class Log:
    """
    simple static method class which setups application loggers

    Attributes:
        DEFAULT_LOG_FORMAT(str): (class attribute) default log format (in case of fallback)
        DEFAULT_LOG_LEVEL(int): (class attribute) default log level (in case of fallback)
    """

    DEFAULT_LOG_FORMAT = "[%(levelname)s %(asctime)s] [%(filename)s:%(lineno)d %(funcName)s]: %(message)s"
    DEFAULT_LOG_LEVEL = logging.DEBUG

    @staticmethod
    def load(configuration: Configuration, *, quiet: bool, report: bool) -> None:
        """
        setup logging settings from configuration

        Args:
            configuration(Configuration): configuration instance
            quiet(bool): force disable any log messages
            report(bool): force enable or disable reporting
        """
        try:
            path = configuration.logging_path
            fileConfig(path)
        except Exception:
            logging.basicConfig(filename=None, format=Log.DEFAULT_LOG_FORMAT,
                                level=Log.DEFAULT_LOG_LEVEL)
            logging.exception("could not load logging from configuration, fallback to stderr")

        HttpLogHandler.load(configuration, report=report)

        if quiet:
            logging.disable(logging.WARNING)  # only print errors here
