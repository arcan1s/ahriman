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
import requests

from functools import cached_property
from typing import Any, IO, Literal

from ahriman import __version__
from ahriman.core.configuration import Configuration
from ahriman.core.log import LazyLogging


# filename, file, content-type, headers
MultipartType = tuple[str, IO[bytes], str, dict[str, str]]


class SyncHttpClient(LazyLogging):
    """
    wrapper around requests library to reduce boilerplate

    Attributes:
        auth(tuple[str, str] | None): HTTP basic auth object if set
        suppress_errors(bool): suppress logging of request errors
        timeout(int): HTTP request timeout in seconds
    """

    def __init__(self, section: str | None = None, configuration: Configuration | None = None, *,
                 suppress_errors: bool = False) -> None:
        """
        default constructor

        Args:
            section(str, optional): settings section name (Default value = None)
            configuration(Configuration | None): configuration instance (Default value = None)
            suppress_errors(bool, optional): suppress logging of request errors (Default value = False)
        """
        if configuration is None:
            configuration = Configuration()  # dummy configuration
        if section is None:
            section = configuration.default_section

        username = configuration.get(section, "username", fallback=None)
        password = configuration.get(section, "password", fallback=None)
        self.auth = (username, password) if username and password else None

        self.timeout = configuration.getint(section, "timeout", fallback=30)
        self.suppress_errors = suppress_errors

    @cached_property
    def session(self) -> requests.Session:
        """
        get or create session

        Returns:
            request.Session: created session object
        """
        session = requests.Session()
        session.headers["User-Agent"] = f"ahriman/{__version__}"

        return session

    @staticmethod
    def exception_response_text(exception: requests.exceptions.RequestException) -> str:
        """
        safe response exception text generation

        Args:
            exception(requests.exceptions.RequestException): exception raised

        Returns:
            str: text of the response if it is not None and empty string otherwise
        """
        result: str = exception.response.text if exception.response is not None else ""
        return result

    def make_request(self, method: Literal["DELETE", "GET", "POST", "PUT"], url: str, *,
                     headers: dict[str, str] | None = None,
                     params: list[tuple[str, str]] | None = None,
                     data: Any | None = None,
                     json: dict[str, Any] | None = None,
                     files: dict[str, MultipartType] | None = None,
                     session: requests.Session | None = None,
                     suppress_errors: bool | None = None) -> requests.Response:
        """
        perform request with specified parameters

        Args:
            method(Literal["DELETE", "GET", "POST", "PUT"]): HTTP method to call
            url(str): remote url to call
            headers(dict[str, str] | None, optional): request headers (Default value = None)
            params(list[tuple[str, str]] | None, optional): request query parameters (Default value = None)
            data(Any | None, optional): request raw data parameters (Default value = None)
            json(dict[str, Any] | None, optional): request json parameters (Default value = None)
            files(dict[str, MultipartType] | None, optional): multipart upload (Default value = None)
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
                                       auth=self.auth, timeout=self.timeout)
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