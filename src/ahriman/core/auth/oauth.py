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
import aioauth_client  # type: ignore

from typing import Optional, Type

from ahriman.core.auth.mapping import Mapping
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import InvalidOption
from ahriman.models.auth_settings import AuthSettings


class OAuth(Mapping):
    """
    OAuth user authorization.
    It is required to create application first and put application credentials.
    :ivar client_id: application client id
    :ivar client_secret: application client secret key
    :ivar provider: provider class, should be one of aiohttp-client provided classes
    :ivar redirect_uri: redirect URI registered in provider
    :ivar scopes: list of scopes required by the application
    """

    def __init__(self, configuration: Configuration, provider: AuthSettings = AuthSettings.OAuth) -> None:
        """
        default constructor
        :param configuration: configuration instance
        :param provider: authorization type definition
        """
        Mapping.__init__(self, configuration, provider)
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
        :return: login control as html code to insert
        """
        return """<a class="nav-link" href="/user-api/v1/login" title="login via OAuth2">login</a>"""

    @staticmethod
    def get_provider(name: str) -> Type[aioauth_client.OAuth2Client]:
        """
        load OAuth2 provider by name
        :param name: name of the provider. Must be valid class defined in aioauth-client library
        :return: loaded provider type
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
        :return: generated client according to current settings
        """
        return self.provider(client_id=self.client_id, client_secret=self.client_secret)

    def get_oauth_url(self) -> str:
        """
        get authorization URI for the specified settings
        :return: authorization URI as a string
        """
        client = self.get_client()
        uri: str = client.get_authorize_url(scope=self.scopes, redirect_uri=self.redirect_uri)
        return uri

    async def get_oauth_username(self, code: str) -> Optional[str]:
        """
        extract OAuth username from remote
        :param code: authorization code provided by external service
        :return: username as is in OAuth provider
        """
        try:
            client = self.get_client()
            access_token, _ = await client.get_access_token(code, redirect_uri=self.redirect_uri)
            client.access_token = access_token

            print(f"HEEELOOOO {client}")
            user, _ = await client.user_info()
            username: str = user.email
            return username
        except Exception:
            self.logger.exception("got exception while performing request")
            return None
