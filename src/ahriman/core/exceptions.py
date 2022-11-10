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
from pathlib import Path
from typing import Any


class BuildError(RuntimeError):
    """
    base exception for failed builds
    """

    def __init__(self, package_base: str) -> None:
        """
        default constructor

        Args:
            package_base(str): package base raised exception
        """
        RuntimeError.__init__(self, f"Package {package_base} build failed, check logs for details")


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
        ValueError.__init__(self, f"Architecture required for subcommand {command}, but missing")


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
        ValueError.__init__(self, f"Multiple architectures are not supported by subcommand {command}")


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
