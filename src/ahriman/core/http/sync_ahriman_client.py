#
# Copyright (c) 2021-2026 ahriman team.
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
import contextlib
import requests

from requests.adapters import BaseAdapter
from urllib.parse import urlparse

from ahriman.core.http.sync_http_client import SyncHttpClient


class SyncAhrimanClient(SyncHttpClient):
    """
    wrapper for ahriman web service

    Attributes:
        address(str): address of the web service
    """

    address: str

    def _login_url(self) -> str:
        """
        get url for the login api

        Returns:
            str: full url for web service to log in
        """
        return f"{self.address}/api/v1/login"

    def adapters(self) -> dict[str, BaseAdapter]:
        """
        get registered adapters

        Returns:
            dict[str, BaseAdapter]: map of protocol and adapter used for this protocol
        """
        adapters = SyncHttpClient.adapters(self)

        if (scheme := urlparse(self.address).scheme) == "http+unix":
            from requests_unixsocket.adapters import UnixAdapter
            adapters[f"{scheme}://"] = UnixAdapter()  # type: ignore[no-untyped-call]

        return adapters

    def on_session_creation(self, session: requests.Session) -> None:
        """
        method which will be called on session creation

        Args:
            session(requests.Session): created requests session
        """
        if self.auth is None:
            return  # no auth configured

        username, password = self.auth
        payload = {
            "username": username,
            "password": password,
        }
        with contextlib.suppress(Exception):
            self.make_request("POST", self._login_url(), json=payload, session=session)
