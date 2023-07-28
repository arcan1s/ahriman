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
from enum import Enum


class LogHandler(str, Enum):
    """
    log handler as described by default configuration

    Attributes:
        Console(LogHandler): (class attribute) write logs to console
        Syslog(LogHandler): (class attribute) write logs to syslog device /dev/null
        Journald(LogHandler): (class attribute) write logs to journald directly
    """

    Console = "console"
    Syslog = "syslog"
    Journald = "journald"