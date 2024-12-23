#
# Copyright (c) 2021-2025 ahriman team.
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

from functools import cached_property
from urllib.parse import urlparse

from ahriman import __version__
from ahriman.core.http.sync_http_client import SyncHttpClient


class SyncAhrimanClient(SyncHttpClient):
    """
    wrapper for ahriman web service

    Attributes:
        address(str): address of the web service
    """

    address: str

    @cached_property
    def session(self) -> requests.Session:
        """
        get or create session

        Returns:
            request.Session: created session object
        """
        if urlparse(self.address).scheme == "http+unix":
            import requests_unixsocket
            session: requests.Session = requests_unixsocket.Session()  # type: ignore[no-untyped-call]
            session.headers["User-Agent"] = f"ahriman/{__version__}"
            return session

        session = requests.Session()
        session.headers["User-Agent"] = f"ahriman/{__version__}"
        self._login(session)

        return session

    def _login(self, session: requests.Session) -> None:
        """
        process login to the service

        Args:
            session(requests.Session): request session to login
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

    def _login_url(self) -> str:
        """
        get url for the login api

        Returns:
            str: full url for web service to log in
        """
        return f"{self.address}/api/v1/login"
