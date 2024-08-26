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
from grp import getgrnam
from pwd import getpwnam

from ahriman.core.auth.mapping import Mapping
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.exceptions import CalledProcessError
from ahriman.core.utils import check_output
from ahriman.models.auth_settings import AuthSettings
from ahriman.models.user_access import UserAccess


class PAM(Mapping):
    """
    User authorization implementation by using default PAM

    Attributes:
        full_access_group(str): group name users of which have full access
        permit_root_login(bool): permit login as root
    """

    def __init__(self, configuration: Configuration, database: SQLite,
                 provider: AuthSettings = AuthSettings.PAM) -> None:
        """
        default constructor

        Args:
            configuration(Configuration): configuration instance
            database(SQLite): database instance
            provider(AuthSettings, optional): authorization type definition (Default value = AuthSettings.PAM)
        """
        Mapping.__init__(self, configuration, database, provider)
        self.full_access_group = configuration.get("auth", "full_access_group")
        self.permit_root_login = configuration.getboolean("auth", "permit_root_login", fallback=False)

    @staticmethod
    def group_members(group_name: str) -> list[str]:
        """
        extract current group members

        Args:
            group_name(str): group name

        Returns:
            list[str]: list of users which belong to the specified group. In case if group wasn't found, the empty list
            will be returned
        """
        try:
            group = getgrnam(group_name)
        except KeyError:
            return []
        return group.gr_mem

    async def check_credentials(self, username: str, password: str | None) -> bool:
        """
        validate user password

        Args:
            username(str): username
            password(str | None): entered password

        Returns:
            bool: ``True`` in case if password matches, ``False`` otherwise
        """
        if password is None:
            return False  # invalid data supplied
        if not self.permit_root_login and username == "root":
            return False  # login as root is not allowed
        # the reason why do we call su here is that python-pam actually read shadow file
        # and hence requires root privileges
        try:
            check_output("su", "--command", "true", "-", username, input_data=password)
            return True
        except CalledProcessError:
            return await Mapping.check_credentials(self, username, password)

    async def known_username(self, username: str) -> bool:
        """
        check if user is known

        Args:
            username(str): username

        Returns:
            bool: ``True`` in case if user is known and can be authorized and ``False`` otherwise
        """
        try:
            _ = getpwnam(username)
            return True
        except KeyError:
            return await Mapping.known_username(self, username)

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
        # this method is basically inverted, first we check overrides in database and then fallback to the PAM logic
        if (user := self.get_user(username)) is not None:
            return user.verify_access(required)
        # if username is in admin group, then we treat it as full access
        if username in self.group_members(self.full_access_group):
            return UserAccess.Full.permits(required)
        # fallback to read-only accounts
        return UserAccess.Read.permits(required)
