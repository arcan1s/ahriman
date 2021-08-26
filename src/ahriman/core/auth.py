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
from typing import Dict, Optional, Set

from ahriman.core.configuration import Configuration
from ahriman.models.user import User
from ahriman.models.user_access import UserAccess


class Auth:
    """
    helper to deal with user authorization
    :ivar allowed_paths: URI paths which can be accessed without authorization
    :ivar allowed_paths_groups: URI paths prefixes which can be accessed without authorization
    :ivar salt: random generated string to salt passwords
    :ivar users: map of username to its descriptor
    :cvar ALLOWED_PATHS: URI paths which can be accessed without authorization, predefined
    :cvar ALLOWED_PATHS_GROUPS: URI paths prefixes which can be accessed without authorization, predefined
    """

    ALLOWED_PATHS = {"/", "/favicon.ico", "/login", "/logout"}
    ALLOWED_PATHS_GROUPS: Set[str] = set()

    def __init__(self, configuration: Configuration) -> None:
        """
        default constructor
        :param configuration: configuration instance
        """
        self.salt = configuration.get("auth", "salt")
        self.users = self.get_users(configuration)

        self.allowed_paths = set(configuration.getlist("auth", "allowed_paths"))
        self.allowed_paths.update(self.ALLOWED_PATHS)
        self.allowed_paths_groups = set(configuration.getlist("auth", "allowed_paths_groups"))
        self.allowed_paths_groups.update(self.ALLOWED_PATHS_GROUPS)

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
        return username in self.users and self.users[username].check_credentials(password, self.salt)

    def is_safe_request(self, uri: Optional[str]) -> bool:
        """
        check if requested path are allowed without authorization
        :param uri: request uri
        :return: True in case if this URI can be requested without authorization and False otherwise
        """
        if uri is None:
            return False  # request without context is not allowed
        return uri in self.ALLOWED_PATHS or any(uri.startswith(path) for path in self.ALLOWED_PATHS_GROUPS)

    def verify_access(self, username: str, required: UserAccess) -> bool:
        """
        validate if user has access to requested resource
        :param username: username
        :param required: required access level
        :return: True in case if user is allowed to do this request and False otherwise
        """
        return username in self.users and self.users[username].verify_access(required)
