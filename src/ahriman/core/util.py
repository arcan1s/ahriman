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
import datetime
import io
import os
import re
import requests
import subprocess

from enum import Enum
from logging import Logger
from pathlib import Path
from typing import Any, Dict, Generator, IO, Iterable, List, Optional, Type, Union

from ahriman.core.exceptions import OptionError, UnsafeRunError
from ahriman.models.repository_paths import RepositoryPaths


__all__ = ["check_output", "check_user", "exception_response_text", "filter_json", "full_version", "enum_values",
           "package_like", "pretty_datetime", "pretty_size", "safe_filename", "walk"]


def check_output(*args: str, exception: Optional[Exception] = None, cwd: Optional[Path] = None,
                 input_data: Optional[str] = None, logger: Optional[Logger] = None, user: Optional[int] = None) -> str:
    """
    subprocess wrapper

    Args:
        *args(str): command line arguments
        exception(Optional[Exception]): exception which has to be reraised instead of default subprocess exception
        cwd(Optional[Path], optional): current working directory (Default value = None)
        input_data(Optional[str], optional): data which will be written to command stdin (Default value = None)
        logger(Optional[Logger], optional): logger to log command result if required (Default value = None)
        user(Optional[int], optional): run process as specified user (Default value = None)

    Returns:
        str: command output

    Raises:
        subprocess.CalledProcessError: if subprocess ended with status code different from 0 and no exception supplied

    Examples:
        Simply call the function::

            >>> check_output("echo", "hello world")

        The more complicated calls which include result logging and input data are also possible::

            >>> import logging
            >>>
            >>> logger = logging.getLogger()
            >>> check_output("python", "-c", "greeting = input('say hello: '); print(); print(greeting)",
            >>>              input_data="hello world", logger=logger)

        An additional argument ``exception`` can be supplied in order to override the default exception::

            >>> check_output("false", exception=RuntimeError("An exception occurred"))
    """
    # hack for Optional[IO[str]] handle
    def get_io(proc: subprocess.Popen[str], channel_name: str) -> IO[str]:
        channel: Optional[IO[str]] = getattr(proc, channel_name, None)
        return channel if channel is not None else io.StringIO()

    def log(single: str) -> None:
        if logger is not None:
            logger.debug(single)

    # FIXME additional workaround for linter and type check which do not know that user arg is supported
    # pylint: disable=unexpected-keyword-arg
    with subprocess.Popen(args, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          user=user, text=True, encoding="utf8", bufsize=1) as process:
        if input_data is not None:
            input_channel = get_io(process, "stdin")
            input_channel.write(input_data)
            input_channel.close()

        # read stdout and append to output result
        result: List[str] = []
        for line in iter(get_io(process, "stdout").readline, ""):
            line = line.strip()
            if not line:  # skip empty lines
                continue
            result.append(line)
            log(line)

        # read stderr and write info to logs
        for line in iter(get_io(process, "stderr").readline, ""):
            log(line.strip())

        process.terminate()  # make sure that process is terminated
        status_code = process.wait()
        if status_code != 0:
            if exception is not None:
                raise exception
            raise subprocess.CalledProcessError(status_code, process.args)

        return "\n".join(result)


def check_user(paths: RepositoryPaths, *, unsafe: bool) -> None:
    """
    check if current user is the owner of the root

    Args:
        paths(RepositoryPaths): repository paths object
        unsafe(bool): if set no user check will be performed before path creation

    Raises:
        UnsafeRun: if root uid differs from current uid and check is enabled

    Examples:
        Simply run function with arguments::

            >>> check_user(paths, unsafe=False)
    """
    if not paths.root.exists():
        return  # no directory found, skip check
    if unsafe:
        return  # unsafe flag is enabled, no check performed
    current_uid = os.getuid()
    root_uid, _ = paths.root_owner
    if current_uid != root_uid:
        raise UnsafeRunError(current_uid, root_uid)


def enum_values(enum: Type[Enum]) -> List[str]:
    """
    generate list of enumeration values from the source

    Args:
        enum(Type[Enum]): source enumeration class

    Returns:
        List[str]: available enumeration values as string
    """
    return [key.value for key in enum]


def exception_response_text(exception: requests.exceptions.HTTPError) -> str:
    """
    safe response exception text generation

    Args:
        exception(requests.exceptions.HTTPError): exception raised

    Returns:
        str: text of the response if it is not None and empty string otherwise
    """
    result: str = exception.response.text if exception.response is not None else ""
    return result


def filter_json(source: Dict[str, Any], known_fields: Iterable[str]) -> Dict[str, Any]:
    """
    filter json object by fields used for json-to-object conversion

    Args:
        source(Dict[str, Any]): raw json object
        known_fields(Iterable[str]): list of fields which have to be known for the target object

    Returns:
        Dict[str, Any]: json object without unknown and empty fields

    Examples:
        This wrapper is mainly used for the dataclasses, thus the flow must be something like this::

            >>> from dataclasses import fields
            >>> from ahriman.models.package import Package
            >>>
            >>> known_fields = [pair.name for pair in fields(Package)]
            >>> properties = filter_json(dump, known_fields)
            >>> package = Package(**properties)
    """
    return {key: value for key, value in source.items() if key in known_fields and value is not None}


def full_version(epoch: Union[str, int, None], pkgver: str, pkgrel: str) -> str:
    """
    generate full version from components

    Args:
        epoch(Union[str, int, None]): package epoch if any
        pkgver(str): package version
        pkgrel(str): package release version (arch linux specific)

    Returns:
        str: generated version
    """
    prefix = f"{epoch}:" if epoch else ""
    return f"{prefix}{pkgver}-{pkgrel}"


def package_like(filename: Path) -> bool:
    """
    check if file looks like package

    Args:
        filename(Path): name of file to check

    Returns:
        bool: True in case if name contains ``.pkg.`` and not signature, False otherwise
    """
    name = filename.name
    return ".pkg." in name and not name.endswith(".sig")


def pretty_datetime(timestamp: Optional[Union[datetime.datetime, float, int]]) -> str:
    """
    convert datetime object to string

    Args:
        timestamp(Optional[Union[datetime.datetime, float, int]]): datetime to convert

    Returns:
        str: pretty printable datetime as string
    """
    if timestamp is None:
        return ""
    if isinstance(timestamp, (int, float)):
        timestamp = datetime.datetime.utcfromtimestamp(timestamp)
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def pretty_size(size: Optional[float], level: int = 0) -> str:
    """
    convert size to string

    Args:
        size(Optional[float]): size to convert
        level(int, optional): represents current units, 0 is B, 1 is KiB, etc (Default value = 0)

    Returns:
        str: pretty printable size as string

    Raises:
        InvalidOption: if size is more than 1TiB
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
        raise OptionError(level)  # must never happen actually

    if size is None:
        return ""
    if size < 1024 or level >= 3:
        return f"{size:.1f} {str_level()}"
    return pretty_size(size / 1024, level + 1)


def safe_filename(source: str) -> str:
    """
    convert source string to its safe representation

    Args:
        source(str): string to convert

    Returns:
        str: result string in which all unsafe characters are replaced by dash
    """
    # RFC-3986 https://datatracker.ietf.org/doc/html/rfc3986 states that unreserved characters are
    # https://datatracker.ietf.org/doc/html/rfc3986#section-2.3
    #     unreserved  = ALPHA / DIGIT / "-" / "." / "_" / "~"
    # however we would like to allow some gen-delims characters in filename, because those characters are used
    # as delimiter in other URI parts. The ones we allow are
    #     ":" - used as separator in schema and userinfo
    #     "[" and "]" - used for host part
    #     "@" - used as separator between host and userinfo
    return re.sub(r"[^A-Za-z\d\-._~:\[\]@]", "-", source)


def walk(directory_path: Path) -> Generator[Path, None, None]:
    """
    list all file paths in given directory
    Credits to https://stackoverflow.com/a/64915960

    Args:
        directory_path(Path): root directory path

    Yields:
        Path: all found files in given directory with full path

    Examples:
        Since the ``pathlib`` module does not provide an alternative to ``os.walk``, this wrapper can be used instead::

            >>> from pathlib import Path
            >>>
            >>> for file_path in walk(Path.cwd()):
            >>>     print(file_path)

        Note, however, that unlike the original method, it does not yield directories.
    """
    for element in directory_path.iterdir():
        if element.is_dir():
            yield from walk(element)
            continue
        yield element
