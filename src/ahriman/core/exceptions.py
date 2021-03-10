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
from typing import Any


class BuildFailed(Exception):
    def __init__(self, package: str) -> None:
        Exception.__init__(self, f'Package {package} build failed, check logs for details')


class InitializeException(Exception):
    def __init__(self) -> None:
        Exception.__init__(self, 'Could not load service')


class InvalidOptionException(Exception):
    def __init__(self, value: Any) -> None:
        Exception.__init__(self, f'Invalid or unknown option value `{value}`')


class InvalidPackageInfo(Exception):
    def __init__(self, details: Any) -> None:
        Exception.__init__(self, f'There are errors during reading package information: `{details}`')


class MissingConfiguration(Exception):
    def __init__(self, name: str) -> None:
        Exception.__init__(self, f'No section `{name}` found')


class ReportFailed(Exception):
    def __init__(self, cause: Exception) -> None:
        Exception.__init__(self, f'Report failed with reason {cause}')


class SyncFailed(Exception):
    def __init__(self, cause: Exception) -> None:
        Exception.__init__(self, f'Sync failed with reason {cause}')