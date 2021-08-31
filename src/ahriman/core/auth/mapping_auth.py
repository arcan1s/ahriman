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
from typing import Dict, Optional

from ahriman.core.auth.auth import Auth
from ahriman.core.configuration import Configuration
from ahriman.models.user import User
from ahriman.models.user_access import UserAccess


class MappingAuth(Auth):
    """
    user authorization based on mapping from configuration file
    :ivar salt: random generated string to salt passwords
    :ivar users: map of username to its descriptor
    """

    def __init__(self, configuration: Configuration) -> None:
        """
        default constructor
        :param configuration: configuration instance
        """
        Auth.__init__(self, configuration)
        self.salt = configuration.get("auth", "salt")
        self.users = self.get_users(configuration)

    @staticmethod
    def get_users(configuration: Configuration) -> Dict[str, User]:
        """
        load users from settings
        :param configuration: configuration instance
        :return: map of username to its descriptor
        """
        users: Dict[str, User] = {}
        for role in UserAccess:
            section = configuration.section_name("auth", role.value)
            if not configuration.has_section(section):
                continue
            for user, password in configuration[section].items():
                users[user] = User(user, password, role)
        return users

    def check_credentials(self, username: Optional[str], password: Optional[str]) -> bool:
        """
        validate user password
        :param username: username
        :param password: entered password
        :return: True in case if password matches, False otherwise
        """
        if username is None or password is None:
            return False  # invalid data supplied
        return self.known_username(username) and self.users[username].check_credentials(password, self.salt)

    def known_username(self, username: str) -> bool:
        """
        check if user is known
        :param username: username
        :return: True in case if user is known and can be authorized and False otherwise
        """
        return username in self.users

    def verify_access(self, username: str, required: UserAccess) -> bool:
        """
        validate if user has access to requested resource
        :param username: username
        :param required: required access level
        :return: True in case if user is allowed to do this request and False otherwise
        """
        return self.known_username(username) and self.users[username].verify_access(required)
