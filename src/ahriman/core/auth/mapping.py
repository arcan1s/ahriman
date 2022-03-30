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
from typing import Optional

from ahriman.core.auth.auth import Auth

from ahriman.core.configuration import Configuration
from ahriman.core.database.sqlite import SQLite
from ahriman.models.auth_settings import AuthSettings
from ahriman.models.user import User
from ahriman.models.user_access import UserAccess


class Mapping(Auth):
    """
    user authorization based on mapping from configuration file
    :ivar salt: random generated string to salt passwords
    :ivar database: database instance
    """

    def __init__(self, configuration: Configuration, database: SQLite,
                 provider: AuthSettings = AuthSettings.Configuration) -> None:
        """
        default constructor
        :param configuration: configuration instance
        :param database: database instance
        :param provider: authorization type definition
        """
        Auth.__init__(self, configuration, provider)
        self.database = database
        self.salt = configuration.get("auth", "salt")

    async def check_credentials(self, username: Optional[str], password: Optional[str]) -> bool:
        """
        validate user password
        :param username: username
        :param password: entered password
        :return: True in case if password matches, False otherwise
        """
        if username is None or password is None:
            return False  # invalid data supplied
        user = self.get_user(username)
        return user is not None and user.check_credentials(password, self.salt)

    def get_user(self, username: str) -> Optional[User]:
        """
        retrieve user from in-memory mapping
        :param username: username
        :return: user descriptor if username is known and None otherwise
        """
        return self.database.user_get(username)

    async def known_username(self, username: Optional[str]) -> bool:
        """
        check if user is known
        :param username: username
        :return: True in case if user is known and can be authorized and False otherwise
        """
        return username is not None and self.get_user(username) is not None

    async def verify_access(self, username: str, required: UserAccess, context: Optional[str]) -> bool:
        """
        validate if user has access to requested resource
        :param username: username
        :param required: required access level
        :param context: URI request path
        :return: True in case if user is allowed to do this request and False otherwise
        """
        user = self.get_user(username)
        return user is not None and user.verify_access(required)
