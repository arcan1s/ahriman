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
from typing import Any


class BuildFailed(Exception):
    """
    base exception for failed builds
    """

    def __init__(self, package: str) -> None:
        """
        default constructor
        :param package: package base raised exception
        """
        Exception.__init__(self, f"Package {package} build failed, check logs for details")


class DuplicateRun(Exception):
    """
    exception which will be raised if there is another application instance
    """

    def __init__(self) -> None:
        """
        default constructor
        """
        Exception.__init__(self, "Another application instance is run")


class InitializeException(Exception):
    """
    base service initialization exception
    """

    def __init__(self) -> None:
        """
        default constructor
        """
        Exception.__init__(self, "Could not load service")


class InvalidOption(Exception):
    """
    exception which will be raised on configuration errors
    """

    def __init__(self, value: Any) -> None:
        """
        default constructor
        :param value: option value
        """
        Exception.__init__(self, f"Invalid or unknown option value `{value}`")


class InvalidPackageInfo(Exception):
    """
    exception which will be raised on package load errors
    """

    def __init__(self, details: Any) -> None:
        """
        default constructor
        :param details: error details
        """
        Exception.__init__(self, f"There are errors during reading package information: `{details}`")


class ReportFailed(Exception):
    """
    report generation exception
    """

    def __init__(self) -> None:
        """
        default constructor
        """
        Exception.__init__(self, "Report failed")


class SyncFailed(Exception):
    """
    remote synchronization exception
    """

    def __init__(self) -> None:
        """
        default constructor
        """
        Exception.__init__(self, "Sync failed")


class UnknownPackage(Exception):
    """
    exception for status watcher which will be thrown on unknown package
    """

    def __init__(self, base: str) -> None:
        Exception.__init__(self, f"Package base {base} is unknown")


class UnsafeRun(Exception):
    """
    exception which will be raised in case if user is not owner of repository
    """

    def __init__(self, current_uid: int, root_uid: int) -> None:
        """
        default constructor
        """
        Exception.__init__(
            self,
            f"""Current UID {current_uid} differs from root owner {root_uid}.
Note that for the most actions it is unsafe to run application as different user.
If you are 100% sure that it must be there try --unsafe option""")
