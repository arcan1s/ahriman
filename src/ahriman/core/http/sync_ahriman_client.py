#
# Copyright (c) 2021-2023 ahriman team.
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
import tenacity

from functools import cached_property
from typing import Any
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
            import requests_unixsocket  # type: ignore[import-untyped]
            session: requests.Session = requests_unixsocket.Session()
            session.headers["User-Agent"] = f"ahriman/{__version__}"
            return session

        session = requests.Session()
        session.headers["User-Agent"] = f"ahriman/{__version__}"
        self._login(session)

        return session

    @staticmethod
    def is_retry_allowed(exception: BaseException) -> bool:
        """
        check if retry is allowed for the exception

        Args:
            exception(BaseException): exception raised

        Returns:
            bool: True in case if exception is in white list and false otherwise
        """
        if not isinstance(exception, requests.RequestException):
            return False  # not a request exception
        status_code = exception.response.status_code if exception.response is not None else None
        return status_code in (401,)

    @staticmethod
    def on_retry(state: tenacity.RetryCallState) -> None:
        """
        action to be called before retry

        Args:
            state(tenacity.RetryCallState): current retry call state
        """
        instance = next(arg for arg in state.args if isinstance(arg, SyncAhrimanClient))
        if hasattr(instance, "session"):  # only if it was initialized
            del instance.session  # clear session

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

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(2),
        retry=tenacity.retry_if_exception(is_retry_allowed),
        after=on_retry,
        reraise=True,
    )
    def make_request(self, *args: Any, **kwargs: Any) -> requests.Response:
        """
        perform request with specified parameters

        Args:
            *args(Any): request method positional arguments
            **kwargs(Any): request method keyword arguments

        Returns:
            requests.Response: response object
        """
        return SyncHttpClient.make_request(self, *args, **kwargs)
