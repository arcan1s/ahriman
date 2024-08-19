#
# Copyright (c) 2021-2024 ahriman team.
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
from ahriman.core.auth import Auth
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.models.auth_settings import AuthSettings
from ahriman.models.user import User
from ahriman.models.user_access import UserAccess


class Mapping(Auth):
    """
    user authorization based on mapping from configuration file

    Attributes:
        salt(str): random generated string to salted password
        database(SQLite): database instance
    """

    def __init__(self, configuration: Configuration, database: SQLite,
                 provider: AuthSettings = AuthSettings.Configuration) -> None:
        """
        default constructor

        Args:
            configuration(Configuration): configuration instance
            database(SQLite): database instance
            provider(AuthSettings, optional): authorization type definition (Default value = AuthSettings.Configuration)
        """
        Auth.__init__(self, configuration, provider)
        self.database = database
        self.salt = configuration.get("auth", "salt", fallback="")

    async def check_credentials(self, username: str, password: str | None) -> bool:
        """
        validate user password

        Args:
            username(str): username
            password(str | None): entered password

        Returns:
            bool: True in case if password matches, False otherwise
        """
        if password is None:
            return False  # invalid data supplied
        user = self.get_user(username)
        return user is not None and user.check_credentials(password, self.salt)

    def get_user(self, username: str) -> User | None:
        """
        retrieve user from in-memory mapping

        Args:
            username(str): username

        Returns:
            User | None: user descriptor if username is known and None otherwise
        """
        return self.database.user_get(username)

    async def known_username(self, username: str) -> bool:
        """
        check if user is known

        Args:
            username(str): username

        Returns:
            bool: True in case if user is known and can be authorized and False otherwise
        """
        return username is not None and self.get_user(username) is not None

    async def verify_access(self, username: str, required: UserAccess, context: str | None) -> bool:
        """
        validate if user has access to requested resource

        Args:
            username(str): username
            required(UserAccess): required access level
            context(str | None): URI request path

        Returns:
            bool: True in case if user is allowed to do this request and False otherwise
        """
        user = self.get_user(username)
        return user is not None and user.verify_access(required)
