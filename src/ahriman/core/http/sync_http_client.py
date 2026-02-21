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
import requests
import sys

from functools import cached_property
from requests.adapters import BaseAdapter, HTTPAdapter
from typing import Any, ClassVar, IO, Literal
from urllib3.util.retry import Retry

from ahriman import __version__
from ahriman.core.configuration import Configuration
from ahriman.core.log import LazyLogging


# filename, file, content-type, headers
MultipartType = tuple[str, IO[bytes], str, dict[str, str]]


class SyncHttpClient(LazyLogging):
    """
    wrapper around requests library to reduce boilerplate

    Attributes:
        DEFAULT_MAX_RETRIES(int): (class attribute) default maximum amount of retries
        DEFAULT_RETRY_BACKOFF(float): (class attribute) default retry exponential backoff
        DEFAULT_TIMEOUT(int | None): (class attribute) default HTTP request timeout in seconds
        auth(tuple[str, str] | None): HTTP basic auth object if set
        retry(Retry): retry policy of the HTTP client
        suppress_errors(bool): suppress logging of request errors
        timeout(int | None): HTTP request timeout in seconds
    """

    DEFAULT_MAX_RETRIES: ClassVar[int] = 0
    DEFAULT_RETRY_BACKOFF: ClassVar[float] = 0.0
    DEFAULT_TIMEOUT: ClassVar[int | None] = 30

    def __init__(self, configuration: Configuration | None = None, section: str | None = None, *,
                 suppress_errors: bool = False) -> None:
        """
        Args:
            configuration(Configuration | None, optional): configuration instance (Default value = None)
            section(str | None, optional): settings section name (Default value = None)
            suppress_errors(bool, optional): suppress logging of request errors (Default value = False)
        """
        configuration = configuration or Configuration()  # dummy configuration
        section = section or configuration.default_section

        username = configuration.get(section, "username", fallback=None)
        password = configuration.get(section, "password", fallback=None)
        self.auth = (username, password) if username and password else None

        self.suppress_errors = suppress_errors

        self.timeout = configuration.getint(section, "timeout", fallback=self.DEFAULT_TIMEOUT)
        self.retry = SyncHttpClient.retry_policy(
            max_retries=configuration.getint(section, "max_retries", fallback=self.DEFAULT_MAX_RETRIES),
            retry_backoff=configuration.getfloat(section, "retry_backoff", fallback=self.DEFAULT_RETRY_BACKOFF),
        )

    @cached_property
    def session(self) -> requests.Session:
        """
        get or create session

        Returns:
            request.Session: created session object
        """
        session = requests.Session()

        for protocol, adapter in self.adapters().items():
            session.mount(protocol, adapter)

        python_version = ".".join(map(str, sys.version_info[:3]))  # just major.minor.patch
        session.headers["User-Agent"] = f"ahriman/{__version__} " \
            f"{requests.utils.default_user_agent()} " \
            f"python/{python_version}"

        self.on_session_creation(session)

        return session

    @staticmethod
    def exception_response_text(exception: requests.RequestException) -> str:
        """
        safe response exception text generation

        Args:
            exception(requests.RequestException): exception raised

        Returns:
            str: text of the response if it is not ``None`` and empty string otherwise
        """
        result: str = exception.response.text if exception.response is not None else ""
        return result

    @staticmethod
    def retry_policy(max_retries: int = 0, retry_backoff: float = 0.0) -> Retry:
        """
        build retry policy for class

        Args:
            max_retries(int, optional): maximum amount of retries allowed (Default value = 0)
            retry_backoff(float, optional): retry exponential backoff (Default value = 0.0)

        Returns:
            Retry: built retry policy
        """
        return Retry(
            total=max_retries,
            connect=max_retries,
            read=max_retries,
            status=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=retry_backoff,
        )

    def adapters(self) -> dict[str, BaseAdapter]:
        """
        get registered adapters

        Returns:
            dict[str, BaseAdapter]: map of protocol and adapter used for this protocol
        """
        return {
            "http://": HTTPAdapter(max_retries=self.retry),
            "https://": HTTPAdapter(max_retries=self.retry),
        }

    def make_request(self, method: Literal["DELETE", "GET", "HEAD", "POST", "PUT"], url: str, *,
                     headers: dict[str, str] | None = None,
                     params: list[tuple[str, str]] | None = None,
                     data: Any | None = None,
                     json: dict[str, Any] | None = None,
                     files: dict[str, MultipartType] | None = None,
                     stream: bool | None = None,
                     session: requests.Session | None = None,
                     suppress_errors: bool | None = None) -> requests.Response:
        """
        perform request with specified parameters

        Args:
            method(Literal["DELETE", "GET", "HEAD", "POST", "PUT"]): HTTP method to call
            url(str): remote url to call
            headers(dict[str, str] | None, optional): request headers (Default value = None)
            params(list[tuple[str, str]] | None, optional): request query parameters (Default value = None)
            data(Any | None, optional): request raw data parameters (Default value = None)
            json(dict[str, Any] | None, optional): request json parameters (Default value = None)
            files(dict[str, MultipartType] | None, optional): multipart upload (Default value = None)
            stream(bool | None, optional): handle response as stream (Default value = None)
            session(requests.Session | None, optional): session object if any (Default value = None)
            suppress_errors(bool | None, optional): suppress logging errors (e.g. if no web server available). If none
                set, the instance-wide value will be used (Default value = None)

        Returns:
            requests.Response: response object
        """
        # defaults
        if suppress_errors is None:
            suppress_errors = self.suppress_errors
        if session is None:
            session = self.session

        try:
            response = session.request(method, url, params=params, data=data, headers=headers, files=files, json=json,
                                       stream=stream, auth=self.auth, timeout=self.timeout)
            response.raise_for_status()
            return response
        except requests.HTTPError as ex:
            if not suppress_errors:
                self.logger.exception("could not perform http request: %s", self.exception_response_text(ex))
            raise
        except Exception:
            if not suppress_errors:
                self.logger.exception("could not perform http request")
            raise

    def on_session_creation(self, session: requests.Session) -> None:
        """
        method which will be called on session creation

        Args:
            session(requests.Session): created requests session
        """
