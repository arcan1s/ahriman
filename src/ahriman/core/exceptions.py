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
import subprocess

from collections.abc import Callable
from pathlib import Path
from typing import Any, Self


class BuildError(RuntimeError):
    """
    base exception for failed builds
    """

    def __init__(self, package_base: str, stderr: str | None = None) -> None:
        """
        default constructor

        Args:
            package_base(str): package base raised exception
            stderr(str | None, optional): stderr of the process if available (Default value = None)
        """
        message = f"Package {package_base} build failed,\n"
        if stderr is not None:
            message += f"process stderr:\n{stderr}\n"
        message += "check logs for details"

        RuntimeError.__init__(self, message)

    @classmethod
    def from_process(cls, package_base: str) -> Callable[[int, list[str], str, str], Self]:
        """
        generate exception callable from process error

        Args:
            package_base(str): package base raised exception

        Returns:
            Callable[[int, list[str], str, str], Self]: exception generator to be passed to subprocess utils
        """
        return lambda code, process, stdout, stderr: cls(package_base, stderr)


class CalledProcessError(subprocess.CalledProcessError):
    """
    like ``subprocess.CalledProcessError``, but better
    """

    def __init__(self, status_code: int, process: list[str], stderr: str) -> None:
        """
        default constructor

        Args:
            status_code(int): process return code
            process(list[str]): process argument list
            stderr(str): stderr of the process
        """
        subprocess.CalledProcessError.__init__(self, status_code, process, stderr=stderr)

    def __str__(self) -> str:
        """
        string representation of the exception

        Returns:
            str: string view of the exception
        """
        return f"""{subprocess.CalledProcessError.__str__(self)}
Process stderr:
{self.stderr}"""


class DuplicateRunError(RuntimeError):
    """
    exception which will be raised if there is another application instance
    """

    def __init__(self) -> None:
        """
        default constructor
        """
        RuntimeError.__init__(
            self, "Another application instance is run. This error can be suppressed by using --force flag.")


class ExitCode(RuntimeError):
    """
    special exception which has to be thrown to return non-zero status without error message
    """


class ExtensionError(RuntimeError):
    """
    exception being raised by trigger load in case of errors
    """


class GitRemoteError(RuntimeError):
    """
    git remote exception
    """

    def __init__(self) -> None:
        """
        default constructor
        """
        RuntimeError.__init__(self, "Git remote failed")


class InitializeError(RuntimeError):
    """
    base service initialization exception
    """

    def __init__(self, details: str) -> None:
        """
        default constructor

        Args:
            details(str): details of the exception
        """
        RuntimeError.__init__(self, f"Could not load service: {details}")


class MigrationError(RuntimeError):
    """
    exception which will be raised on migration error
    """

    def __init__(self, details: str) -> None:
        """
        default constructor

        Args:
            details(str): error details
        """
        RuntimeError.__init__(self, details)


class MissingArchitectureError(ValueError):
    """
    exception which will be raised if architecture is required, but missing
    """

    def __init__(self, command: str) -> None:
        """
        default constructor

        Args:
            command(str): command name which throws exception
        """
        ValueError.__init__(self, f"Architecture/repository required for subcommand {command}, but missing")


class MultipleArchitecturesError(ValueError):
    """
    exception which will be raised if multiple architectures are not supported by the handler
    """

    def __init__(self, command: str) -> None:
        """
        default constructor

        Args:
            command(str): command name which throws exception
        """
        ValueError.__init__(self, f"Multiple architectures/repositories are not supported by subcommand {command}")


class OptionError(ValueError):
    """
    exception which will be raised on configuration errors
    """

    def __init__(self, value: Any) -> None:
        """
        default constructor

        Args:
            value(Any): option value
        """
        ValueError.__init__(self, f"Invalid or unknown option value `{value}`")


class PackageInfoError(RuntimeError):
    """
    exception which will be raised on package load errors
    """

    def __init__(self, details: Any) -> None:
        """
        default constructor

        Args:
            details(Any): error details
        """
        RuntimeError.__init__(self, f"There are errors during reading package information: `{details}`")


class PathError(ValueError):
    """
    exception which will be raised on path which is not belong to root directory
    """

    def __init__(self, path: Path, root: Path) -> None:
        """
        default constructor

        Args:
            path(Path): path which raised an exception
            root(Path): repository root (i.e. ahriman home)
        """
        ValueError.__init__(self, f"Path `{path}` does not belong to repository root `{root}`")


class PasswordError(ValueError):
    """
    exception which will be raised in case of password related errors
    """

    def __init__(self, details: Any) -> None:
        """
        default constructor

        Args:
            details(Any); error details
        """
        ValueError.__init__(self, f"Password error: {details}")


class PartitionError(RuntimeError):
    """
    exception raised during packages partition actions
    """

    def __init__(self, count: int) -> None:
        """
        default constructor

        Args:
            count(int): count of partitions
        """
        RuntimeError.__init__(self, f"Could not divide packages into {count} partitions")


class PkgbuildGeneratorError(RuntimeError):
    """
    exception class for support type triggers
    """

    def __init__(self) -> None:
        """
        default constructor
        """
        RuntimeError.__init__(self, "Could not generate package")


class ReportError(RuntimeError):
    """
    report generation exception
    """

    def __init__(self) -> None:
        """
        default constructor
        """
        RuntimeError.__init__(self, "Report failed")


class SynchronizationError(RuntimeError):
    """
    remote synchronization exception
    """

    def __init__(self) -> None:
        """
        default constructor
        """
        RuntimeError.__init__(self, "Sync failed")


class UnknownPackageError(ValueError):
    """
    exception for status watcher which will be thrown on unknown package
    """

    def __init__(self, package_base: str) -> None:
        """
        default constructor

        Args:
            package_base(str): package base name
        """
        ValueError.__init__(self, f"Package base {package_base} is unknown")


class UnprocessedPackageStatusError(ValueError):
    """
    exception for merging invalid statues
    """

    def __init__(self, package_base: str) -> None:
        """
        default constructor

        Args:
            package_base(str): package base name
        """
        ValueError.__init__(self, f"Package base {package_base} had status failed, but new status is success")


class UnsafeRunError(RuntimeError):
    """
    exception which will be raised in case if user is not owner of repository
    """

    def __init__(self, current_uid: int, root_uid: int) -> None:
        """
        default constructor

        Args:
            current_uid(int): current user ID
            root_uid(int): ID of the owner of root directory
        """
        RuntimeError.__init__(self, f"Current UID {current_uid} differs from root owner {root_uid}. "
                                    f"Note that for the most actions it is unsafe to run application as different user."
                                    f" If you are 100% sure that it must be there try --unsafe option")
