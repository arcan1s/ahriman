#
# Copyright (c) 2021 ahriman team.
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
import requests

from logging import Logger
from pathlib import Path
from typing import Optional, Union

from ahriman.core.exceptions import InvalidOption


def check_output(*args: str, exception: Optional[Exception], cwd: Optional[Path] = None,
                 input_data: Optional[str] = None, logger: Optional[Logger] = None) -> str:
    """
    subprocess wrapper
    :param args: command line arguments
    :param exception: exception which has to be reraised instead of default subprocess exception
    :param cwd: current working directory
    :param input_data: data which will be written to command stdin
    :param logger: logger to log command result if required
    :return: command output
    """
    try:
        # universal_newlines is required to read input from string
        result: str = subprocess.check_output(args, cwd=cwd, input=input_data, stderr=subprocess.STDOUT,
                                              universal_newlines=True).strip()
        if logger is not None:
            for line in result.splitlines():
                logger.debug(line)
    except subprocess.CalledProcessError as e:
        if e.output is not None and logger is not None:
            for line in e.output.splitlines():
                logger.debug(line)
        raise exception or e
    return result


def exception_response_text(exception: requests.exceptions.HTTPError) -> str:
    """
    safe response exception text generation
    :param exception: exception raised
    :return: text of the response if it is not None and empty string otherwise
    """
    result: str = exception.response.text if exception.response is not None else ""
    return result


def package_like(filename: Path) -> bool:
    """
    check if file looks like package
    :param filename: name of file to check
    :return: True in case if name contains `.pkg.` and not signature, False otherwise
    """
    name = filename.name
    return ".pkg." in name and not name.endswith(".sig")


def pretty_datetime(timestamp: Optional[Union[float, int]]) -> str:
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
        raise InvalidOption(level)  # must never happen actually

    if size is None:
        return ""
    if size < 1024 or level >= 3:
        return f"{size:.1f} {str_level()}"
    return pretty_size(size / 1024, level + 1)
