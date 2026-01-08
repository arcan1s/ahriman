#
# Copyright (c) 2021-2026 ahriman team.
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
import bcrypt

from dataclasses import dataclass, replace
from secrets import token_urlsafe as generate_password
from typing import ClassVar, Self

from ahriman.models.user_access import UserAccess


@dataclass(frozen=True, kw_only=True)
class User:
    """
    authorized web user model

    Attributes:
        SUPPORTED_ALGOS(set[str]): (class attribute) list of the supported hashing algorithms
        username(str): username
        password(str): hashed user password with salt
        access(UserAccess): user role
        packager_id(str | None): packager id to be used. If not set, the default service packager will be used
        key(str | None): personal packager key if any. If user id is empty, it is interpreted as default key

    Examples:
        Simply create user from database data and perform required validation::

            >>> password = User.generate_password(24)
            >>> user = User(username="ahriman", password=password, access=UserAccess.Full)

        Since the password supplied may be plain text, the :func:`hash_password()` method can be used to hash
        the password::

            >>> user = user.hash_password("salt")

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
    packager_id: str | None = None
    key: str | None = None

    SUPPORTED_ALGOS: ClassVar[set[str]] = {"$2$", "$2a$", "$2x$", "$2y$", "$2b$"}

    def __post_init__(self) -> None:
        """
        remove empty fields
        """
        object.__setattr__(self, "packager_id", self.packager_id or None)
        object.__setattr__(self, "key", self.key or None)

    @property
    def algo(self) -> str | None:
        """
        extract algorithm used for the hashing password

        Returns:
            str | None: first part of password hash (e.g. ``$2$``) if available or ``None`` otherwise
        """
        if not self.password:
            return None
        algo = next(segment for segment in self.password.split("$") if segment)
        return f"${algo}$"

    @staticmethod
    def generate_password(length: int) -> str:
        """
        generate password with specified length

        Args:
            length(int): password length

        Returns:
            str: random string which contains letters and numbers
        """
        return generate_password(length)[:length]

    def check_credentials(self, password: str, salt: str) -> bool:
        """
        validate user password

        Args:
            password(str): entered password
            salt(str): salt for hashed password

        Returns:
            bool: ``True`` in case if password matches, ``False`` otherwise

        Raises:
            ValueError: if user password is set to unsupported algorithm
        """
        if (algo := self.algo) is not None and algo not in self.SUPPORTED_ALGOS:
            raise ValueError(f"Crypt {algo} is not supported, consider setting new password")
        try:
            return bcrypt.checkpw((password + salt).encode("utf8"), self.password.encode("utf8"))
        except ValueError:
            return False  # the absence of evidence is not the evidence of absence (c) Gin Rummy

    def hash_password(self, salt: str) -> Self:
        """
        generate hashed password from plain text

        Args:
            salt(str): salt for hashed password

        Returns:
            Self: user with hashed password to store in configuration
        """
        if not self.password:
            # in case of empty password we leave it empty. This feature is used by any external (like OAuth) provider
            # when we do not store any password here
            return self
        password_hash = bcrypt.hashpw((self.password + salt).encode("utf8"), bcrypt.gensalt())
        return replace(self, password=password_hash.decode("utf8"))

    def verify_access(self, required: UserAccess) -> bool:
        """
        validate if user has access to requested resource

        Args:
            required(UserAccess): required access level

        Returns:
            bool: ``True`` in case if user is allowed to do this request and ``False`` otherwise
        """
        return self.access.permits(required)

    def __repr__(self) -> str:
        """
        generate string representation of object

        Returns:
            str: unique string representation
        """
        return f"User(username={self.username}, access={self.access}, packager_id={self.packager_id}, key={self.key})"
