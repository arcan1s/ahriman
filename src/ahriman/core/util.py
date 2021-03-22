#
# Copyright (c) 2021 Evgenii Alekseev.
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
import datetime
import subprocess

from logging import Logger
from pathlib import Path
from typing import Optional

from ahriman.core.exceptions import InvalidOption


def check_output(*args: str, exception: Optional[Exception],
                 cwd: Optional[Path] = None, stderr: int = subprocess.STDOUT,
                 logger: Optional[Logger] = None) -> str:
    """
    subprocess wrapper
    :param args: command line arguments
    :param exception: exception which has to be reraised instead of default subprocess exception
    :param cwd: current working directory
    :param stderr: standard error output mode
    :param logger: logger to log command result if required
    :return: command output
    """
    try:
        result = subprocess.check_output(args, cwd=cwd, stderr=stderr).decode("utf8").strip()
        if logger is not None:
            for line in result.splitlines():
                logger.debug(line)
    except subprocess.CalledProcessError as e:
        if e.output is not None and logger is not None:
            for line in e.output.decode("utf8").splitlines():
                logger.debug(line)
        raise exception or e
    return result


def package_like(filename: str) -> bool:
    """
    check if file looks like package
    :param filename: name of file to check
    :return: True in case if name contains `.pkg.` and not signature, False otherwise
    """
    return ".pkg." in filename and not filename.endswith(".sig")


def pretty_datetime(timestamp: Optional[int]) -> str:
    """
    convert datetime object to string
    :param timestamp: datetime to convert
    :return: pretty printable datetime as string
    """
    return "" if timestamp is None else datetime.datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def pretty_size(size: Optional[float], level: int = 0) -> str:
    """
    convert size to string
    :param size: size to convert
    :param level: represents current units, 0 is B, 1 is KiB etc
    :return: pretty printable size as string
    """
    def str_level() -> str:
        if level == 0:
            return "B"
        if level == 1:
            return "KiB"
        if level == 2:
            return "MiB"
        if level == 3:
            return "GiB"
        raise InvalidOption(level)  # I hope it will not be more than 1024 GiB

    if size is None:
        return ""
    if size < 1024:
        return f"{round(size, 2)} {str_level()}"
    return pretty_size(size / 1024, level + 1)
