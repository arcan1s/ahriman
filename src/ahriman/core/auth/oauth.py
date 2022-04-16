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
import aioauth_client

from typing import Optional, Type

from ahriman.core.auth.mapping import Mapping
from ahriman.core.configuration import Configuration
from ahriman.core.database.sqlite import SQLite
from ahriman.core.exceptions import InvalidOption
from ahriman.models.auth_settings import AuthSettings


class OAuth(Mapping):
    """
    OAuth user authorization.
    It is required to create application first and put application credentials.

    Attributes:
      client_id(str): application client id
      client_secret(str): application client secret key
      provider(aioauth_client.OAuth2Client): provider class, should be one of aiohttp-client provided classes
      redirect_uri(str): redirect URI registered in provider
      scopes(str): list of scopes required by the application
    """

    def __init__(self, configuration: Configuration, database: SQLite,
                 provider: AuthSettings = AuthSettings.OAuth) -> None:
        """
        default constructor

        Args:
          configuration(Configuration): configuration instance
          database(SQLite): database instance
          provider(AuthSettings, optional): authorization type definition (Default value = AuthSettings.OAuth)
        """
        Mapping.__init__(self, configuration, database, provider)
        self.client_id = configuration.get("auth", "client_id")
        self.client_secret = configuration.get("auth", "client_secret")
        # in order to use OAuth feature the service must be publicity available
        # thus we expect that address is set
        self.redirect_uri = f"""{configuration.get("web", "address")}/user-api/v1/login"""
        self.provider = self.get_provider(configuration.get("auth", "oauth_provider"))
        # it is list but we will have to convert to string it anyway
        self.scopes = configuration.get("auth", "oauth_scopes")

    @property
    def auth_control(self) -> str:
        """
        Returns:
          str: login control as html code to insert
        """
        return """<a class="nav-link" href="/user-api/v1/login" title="login via OAuth2">login</a>"""

    @staticmethod
    def get_provider(name: str) -> Type[aioauth_client.OAuth2Client]:
        """
        load OAuth2 provider by name

        Args:
          name(str): name of the provider. Must be valid class defined in aioauth-client library

        Returns:
          Type[aioauth_client.OAuth2Client]: loaded provider type
        """
        provider: Type[aioauth_client.OAuth2Client] = getattr(aioauth_client, name)
        try:
            is_oauth2_client = issubclass(provider, aioauth_client.OAuth2Client)
        except TypeError:  # what if it is random string?
            is_oauth2_client = False
        if not is_oauth2_client:
            raise InvalidOption(name)
        return provider

    def get_client(self) -> aioauth_client.OAuth2Client:
        """
        load client from parameters

        Returns:
          aioauth_client.OAuth2Client: generated client according to current settings
        """
        return self.provider(client_id=self.client_id, client_secret=self.client_secret)

    def get_oauth_url(self) -> str:
        """
        get authorization URI for the specified settings

        Returns:
          str: authorization URI as a string
        """
        client = self.get_client()
        uri: str = client.get_authorize_url(scope=self.scopes, redirect_uri=self.redirect_uri)
        return uri

    async def get_oauth_username(self, code: str) -> Optional[str]:
        """
        extract OAuth username from remote

        Args:
          code(str): authorization code provided by external service

        Returns:
          Optional[str]: username as is in OAuth provider
        """
        try:
            client = self.get_client()
            access_token, _ = await client.get_access_token(code, redirect_uri=self.redirect_uri)
            client.access_token = access_token

            user, _ = await client.user_info()
            username: str = user.email  # type: ignore
            return username
        except Exception:
            self.logger.exception("got exception while performing request")
            return None
