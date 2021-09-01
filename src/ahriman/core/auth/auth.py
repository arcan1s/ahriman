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

from typing import Optional, Set, Type

from ahriman.core.configuration import Configuration
from ahriman.models.user_access import UserAccess


class Auth:
    """
    helper to deal with user authorization
    :ivar allowed_paths: URI paths which can be accessed without authorization
    :ivar allowed_paths_groups: URI paths prefixes which can be accessed without authorization
    :ivar enabled: indicates if authorization is enabled
    :cvar ALLOWED_PATHS: URI paths which can be accessed without authorization, predefined
    :cvar ALLOWED_PATHS_GROUPS: URI paths prefixes which can be accessed without authorization, predefined
    """

    ALLOWED_PATHS = {"/", "/favicon.ico", "/index.html", "/login", "/logout"}
    ALLOWED_PATHS_GROUPS: Set[str] = set()

    def __init__(self, configuration: Configuration) -> None:
        """
        default constructor
        :param configuration: configuration instance
        """
        self.allowed_paths = set(configuration.getlist("auth", "allowed_paths"))
        self.allowed_paths.update(self.ALLOWED_PATHS)
        self.allowed_paths_groups = set(configuration.getlist("auth", "allowed_paths_groups"))
        self.allowed_paths_groups.update(self.ALLOWED_PATHS_GROUPS)
        self.enabled = configuration.getboolean("auth", "enabled", fallback=False)

    @classmethod
    def load(cls: Type[Auth], configuration: Configuration) -> Auth:
        """
        load authorization module from settings
        :param configuration: configuration instance
        :return: authorization module according to current settings
        """
        if configuration.getboolean("auth", "enabled", fallback=False):
            from ahriman.core.auth.mapping_auth import MappingAuth
            return MappingAuth(configuration)
        return cls(configuration)

    def check_credentials(self, username: Optional[str], password: Optional[str]) -> bool:  # pylint: disable=no-self-use
        """
        validate user password
        :param username: username
        :param password: entered password
        :return: True in case if password matches, False otherwise
        """
        del username, password
        return True

    def is_safe_request(self, uri: Optional[str]) -> bool:
        """
        check if requested path are allowed without authorization
        :param uri: request uri
        :return: True in case if this URI can be requested without authorization and False otherwise
        """
        if not uri:
            return False  # request without context is not allowed
        return uri in self.allowed_paths or any(uri.startswith(path) for path in self.allowed_paths_groups)

    def known_username(self, username: str) -> bool:  # pylint: disable=no-self-use
        """
        check if user is known
        :param username: username
        :return: True in case if user is known and can be authorized and False otherwise
        """
        del username
        return True

    def verify_access(self, username: str, required: UserAccess) -> bool:  # pylint: disable=no-self-use
        """
        validate if user has access to requested resource
        :param username: username
        :param required: required access level
        :return: True in case if user is allowed to do this request and False otherwise
        """
        del username, required
        return True
