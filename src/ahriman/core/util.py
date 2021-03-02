import subprocess

from logging import Logger
from typing import Optional


def check_output(*args: str, exception: Optional[Exception],
                 cwd = None, stderr: int = subprocess.STDOUT,
                 logger: Optional[Logger] = None) -> str:
    try:
        result = subprocess.check_output(args, cwd=cwd, stderr=stderr).decode('utf8').strip()
        if logger is not None:
            for line in result.splitlines():
                logger.debug(line)
    except subprocess.CalledProcessError as e:
        if e.output is not None and logger is not None:
            for line in e.output.decode('utf8').splitlines():
                logger.debug(line)
        raise exception or e
    return result