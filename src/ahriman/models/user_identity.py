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
from __future__ import annotations

import time

from dataclasses import dataclass
from typing import Optional, Type


@dataclass
class UserIdentity:
    """
    user identity used inside web service
    :ivar username: username
    :ivar expire_at: identity expiration timestamp
    """

    username: str
    expire_at: int

    @classmethod
    def from_identity(cls: Type[UserIdentity], identity: str) -> Optional[UserIdentity]:
        """
        parse identity into object
        :param identity: identity from session data
        :return: user identity object if it can be parsed and not expired and None otherwise
        """
        try:
            username, expire_at = identity.split()
            user = cls(username, int(expire_at))
            return None if user.is_expired() else user
        except ValueError:
            return None

    @classmethod
    def from_username(cls: Type[UserIdentity], username: Optional[str], max_age: int) -> Optional[UserIdentity]:
        """
        generate identity from username
        :param username: username
        :param max_age: time to expire, seconds
        :return: constructed identity object
        """
        return cls(username, cls.expire_when(max_age)) if username is not None else None

    @staticmethod
    def expire_when(max_age: int) -> int:
        """
        generate expiration time using delta
        :param max_age: time delta to generate. Must be usually TTE
        :return: expiration timestamp
        """
        return int(time.time()) + max_age

    def is_expired(self) -> bool:
        """
        compare timestamp with current timestamp and return True in case if identity is expired
        :return: True in case if identity is expired and False otherwise
        """
        return self.expire_when(0) > self.expire_at

    def to_identity(self) -> str:
        """
        convert object to identity representation
        :return: web service identity
        """
        return f"{self.username} {self.expire_at}"
