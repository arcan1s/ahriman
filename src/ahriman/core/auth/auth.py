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
from __future__ import annotations

from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.log import LazyLogging
from ahriman.models.auth_settings import AuthSettings
from ahriman.models.user_access import UserAccess


class Auth(LazyLogging):
    """
    helper to deal with user authorization

    Attributes:
        enabled(bool): indicates if authorization is enabled
        max_age(int): session age in seconds. It will be used for both client side and server side checks
        allow_read_only(bool): allow read only access to APIs
    """

    def __init__(self, configuration: Configuration, provider: AuthSettings = AuthSettings.Disabled) -> None:
        """
        Args:
            configuration(Configuration): configuration instance
            provider(AuthSettings, optional): authorization type definition (Default value = AuthSettings.Disabled)
        """
        self.allow_read_only = configuration.getboolean("auth", "allow_read_only")

        self.enabled = provider.is_enabled
        self.max_age = configuration.getint("auth", "max_age", fallback=7 * 24 * 3600)

    @property
    def auth_control(self) -> str:
        """
        This workaround is required to make different behaviour for login interface.
        In case of internal authentication it must provide an interface (modal form) to log in with button sends POST
        request. But for an external providers behaviour can be different: e.g. OAuth provider requires sending GET
        request to external resource

        Returns:
            str: login control as html code to insert
        """
        return """<button type="button" class="btn btn-link" data-bs-toggle="modal" data-bs-target="#login-modal" style="text-decoration: none"><i class="bi bi-box-arrow-in-right"></i> login</button>"""

    @staticmethod
    def load(configuration: Configuration, database: SQLite) -> Auth:
        """
        load authorization module from settings

        Args:
            configuration(Configuration): configuration instance
            database(SQLite): database instance

        Returns:
            Auth: authorization module according to current settings
        """
        match AuthSettings.from_option(configuration.get("auth", "target", fallback="disabled")):
            case AuthSettings.Configuration:
                from ahriman.core.auth.mapping import Mapping
                return Mapping(configuration, database)
            case AuthSettings.OAuth:
                from ahriman.core.auth.oauth import OAuth
                return OAuth(configuration, database)
            case AuthSettings.PAM:
                from ahriman.core.auth.pam import PAM
                return PAM(configuration, database)
            case _:
                return Auth(configuration)

    async def check_credentials(self, username: str, password: str | None) -> bool:
        """
        validate user password

        Args:
            username(str): username
            password(str | None): entered password

        Returns:
            bool: ``True`` in case if password matches, ``False`` otherwise
        """
        del username, password
        return True

    async def known_username(self, username: str) -> bool:
        """
        check if user is known

        Args:
            username(str): username

        Returns:
            bool: ``True`` in case if user is known and can be authorized and ``False`` otherwise
        """
        del username
        return True

    async def verify_access(self, username: str, required: UserAccess, context: str | None) -> bool:
        """
        validate if user has access to requested resource

        Args:
            username(str): username
            required(UserAccess): required access level
            context(str | None): URI request path

        Returns:
            bool: ``True`` in case if user is allowed to do this request and ``False`` otherwise
        """
        del username, required, context
        return True
