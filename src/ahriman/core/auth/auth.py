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

import logging

from typing import Dict, Optional, Type

from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import DuplicateUser
from ahriman.models.auth_settings import AuthSettings
from ahriman.models.user import User
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

    ALLOWED_PATHS = {"/", "/index.html"}
    ALLOWED_PATHS_GROUPS = {"/static", "/user-api"}

    def __init__(self, configuration: Configuration, provider: AuthSettings = AuthSettings.Disabled) -> None:
        """
        default constructor
        :param configuration: configuration instance
        :param provider: authorization type definition
        """
        self.logger = logging.getLogger("http")

        self.allow_read_only = configuration.getboolean("auth", "allow_read_only")
        self.allowed_paths = set(configuration.getlist("auth", "allowed_paths"))
        self.allowed_paths.update(self.ALLOWED_PATHS)
        self.allowed_paths_groups = set(configuration.getlist("auth", "allowed_paths_groups"))
        self.allowed_paths_groups.update(self.ALLOWED_PATHS_GROUPS)
        self.enabled = provider.is_enabled
        self.max_age = configuration.getint("auth", "max_age", fallback=7 * 24 * 3600)

    @property
    def auth_control(self) -> str:
        """
        This workaround is required to make different behaviour for login interface.
        In case of internal authentication it must provide an interface (modal form) to login with button sends POST
        request. But for an external providers behaviour can be different: e.g. OAuth provider requires sending GET
        request to external resource
        :return: login control as html code to insert
        """
        return """<button type="button" class="btn btn-link" data-bs-toggle="modal" data-bs-target="#loginForm" style="text-decoration: none">login</button>"""

    @classmethod
    def load(cls: Type[Auth], configuration: Configuration) -> Auth:
        """
        load authorization module from settings
        :param configuration: configuration instance
        :return: authorization module according to current settings
        """
        provider = AuthSettings.from_option(configuration.get("auth", "target", fallback="disabled"))
        if provider == AuthSettings.Configuration:
            from ahriman.core.auth.mapping import Mapping
            return Mapping(configuration)
        if provider == AuthSettings.OAuth:
            from ahriman.core.auth.oauth import OAuth
            return OAuth(configuration)
        return cls(configuration)

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
                normalized_user = user.lower()
                if normalized_user in users:
                    raise DuplicateUser(normalized_user)
                users[normalized_user] = User(normalized_user, password, role)
        return users

    async def check_credentials(self, username: Optional[str], password: Optional[str]) -> bool:  # pylint: disable=no-self-use
        """
        validate user password
        :param username: username
        :param password: entered password
        :return: True in case if password matches, False otherwise
        """
        del username, password
        return True

    async def is_safe_request(self, uri: Optional[str], required: UserAccess) -> bool:
        """
        check if requested path are allowed without authorization
        :param uri: request uri
        :param required: required access level
        :return: True in case if this URI can be requested without authorization and False otherwise
        """
        if required == UserAccess.Read and self.allow_read_only:
            return True  # in case if read right requested and allowed in options
        if not uri:
            return False  # request without context is not allowed
        return uri in self.allowed_paths or any(uri.startswith(path) for path in self.allowed_paths_groups)

    async def known_username(self, username: Optional[str]) -> bool:  # pylint: disable=no-self-use
        """
        check if user is known
        :param username: username
        :return: True in case if user is known and can be authorized and False otherwise
        """
        del username
        return True

    async def verify_access(self, username: str, required: UserAccess, context: Optional[str]) -> bool:  # pylint: disable=no-self-use
        """
        validate if user has access to requested resource
        :param username: username
        :param required: required access level
        :param context: URI request path
        :return: True in case if user is allowed to do this request and False otherwise
        """
        del username, required, context
        return True
