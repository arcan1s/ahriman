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
from __future__ import annotations

from enum import Enum, auto

from ahriman.core.exceptions import InvalidOptionException


class SignSettings(Enum):
    Disabled = auto()
    SignPackages = auto()
    SignRepository = auto()

    @staticmethod
    def from_option(value: str) -> SignSettings:
        if value.lower() in ('no', 'disabled'):
            return SignSettings.Disabled
        elif value.lower() in ('package', 'packages', 'sign-package'):
            return SignSettings.SignPackages
        elif value.lower() in ('repository', 'sign-repository'):
            return SignSettings.SignRepository
        raise InvalidOptionException(value)