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

from dataclasses import dataclass, replace
from typing import Optional, Type
from passlib.pwd import genword as generate_password
from passlib.handlers.sha2_crypt import sha512_crypt

from ahriman.models.user_access import UserAccess


@dataclass(frozen=True, kw_only=True)
class User:
    """
    authorized web user model

    Attributes:
        username(str): username
        password(str): hashed user password with salt
        access(UserAccess): user role

    Examples:
        Simply create user from database data and perform required validation::

            >>> password = User.generate_password(24)
            >>> user = User("ahriman", password, UserAccess.Write)

        Since the password supplied may be plain text, the ``hash_password`` method can be used to hash the password::

            >>> user.password = user.hash_password("salt")

        Having the user instance and password, it can be validated::

            >>> if user.check_credentials(password, "salt"):
            >>>     print("password is valid")
            >>> else:
            >>>     print("password is invalid")

        ...and finally access can be verified::

            >>> if user.verify_access(UserAccess.Read):
            >>>     print(f"user {user.username} has read access")
    """

    username: str
    password: str
    access: UserAccess

    _HASHER = sha512_crypt

    @classmethod
    def from_option(cls: Type[User], username: Optional[str], password: Optional[str],
                    access: UserAccess = UserAccess.Read) -> Optional[User]:
        """
        build user descriptor from configuration options

        Args:
            username(Optional[str]): username
            password(Optional[str]): password as string
            access(UserAccess, optional): optional user access (Default value = UserAccess.Read)

        Returns:
            Optional[User]: generated user descriptor if all options are supplied and None otherwise
        """
        if username is None or password is None:
            return None
        return cls(username=username, password=password, access=access)

    @staticmethod
    def generate_password(length: int) -> str:
        """
        generate password with specified length

        Args:
            length(int): password length

        Returns:
            str: random string which contains letters and numbers
        """
        password: str = generate_password(length=length)
        return password

    def check_credentials(self, password: str, salt: str) -> bool:
        """
        validate user password

        Args:
            password(str): entered password
            salt(str): salt for hashed password

        Returns:
            bool: True in case if password matches, False otherwise
        """
        try:
            verified: bool = self._HASHER.verify(password + salt, self.password)
        except ValueError:
            verified = False  # the absence of evidence is not the evidence of absence (c) Gin Rummy
        return verified

    def hash_password(self, salt: str) -> User:
        """
        generate hashed password from plain text

        Args:
            salt(str): salt for hashed password

        Returns:
            User: user with hashed password to store in configuration
        """
        if not self.password:
            # in case of empty password we leave it empty. This feature is used by any external (like OAuth) provider
            # when we do not store any password here
            return self
        password_hash: str = self._HASHER.hash(self.password + salt)
        return replace(self, password=password_hash)

    def verify_access(self, required: UserAccess) -> bool:
        """
        validate if user has access to requested resource

        Args:
            required(UserAccess): required access level

        Returns:
            bool: True in case if user is allowed to do this request and False otherwise
        """
        return self.access.permits(required)

    def __repr__(self) -> str:
        """
        generate string representation of object

        Returns:
            str: unique string representation
        """
        return f"User(username={self.username}, access={self.access})"
