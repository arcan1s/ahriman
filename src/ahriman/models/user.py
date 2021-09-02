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
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Type
from passlib.pwd import genword as generate_password  # type: ignore
from passlib.handlers.sha2_crypt import sha512_crypt  # type: ignore

from ahriman.models.user_access import UserAccess


@dataclass
class User:
    """
    authorized web user model
    :ivar username: username
    :ivar password: hashed user password with salt
    :ivar access: user role
    """
    username: str
    password: str
    access: UserAccess

    _HASHER = sha512_crypt

    @classmethod
    def from_option(cls: Type[User], username: Optional[str], password: Optional[str]) -> Optional[User]:
        """
        build user descriptor from configuration options
        :param username: username
        :param password: password as string
        :return: generated user descriptor if all options are supplied and None otherwise
        """
        if username is None or password is None:
            return None
        return cls(username, password, UserAccess.Status)

    @staticmethod
    def generate_password(length: int) -> str:
        """
        generate password with specified length
        :param length: password length
        :return: random string which contains letters and numbers
        """
        password: str = generate_password(length=length)
        return password

    def check_credentials(self, password: str, salt: str) -> bool:
        """
        validate user password
        :param password: entered password
        :param salt: salt for hashed password
        :return: True in case if password matches, False otherwise
        """
        verified: bool = self._HASHER.verify(password + salt, self.password)
        return verified

    def hash_password(self, password: str, salt: str) -> str:
        """
        generate hashed password from plain text
        :param password: entered password
        :param salt: salt for hashed password
        :return: hashed string to store in configuration
        """
        password_hash: str = self._HASHER.hash(password + salt)
        return password_hash

    def verify_access(self, required: UserAccess) -> bool:
        """
        validate if user has access to requested resource
        :param required: required access level
        :return: True in case if user is allowed to do this request and False otherwise
        """
        if self.access == UserAccess.Write:
            return True  # everything is allowed
        return self.access == required

    def __repr__(self) -> str:
        """
        generate string representation of object
        :return: unique string representation
        """
        return f"User(username={self.username}, access={self.access})"
