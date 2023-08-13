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
import logging
import requests

from collections.abc import Generator
from typing import Any, Literal
from urllib.parse import quote_plus as urlencode

from ahriman import __version__
from ahriman.core.configuration import Configuration
from ahriman.core.log import LazyLogging
from ahriman.core.status.client import Client
from ahriman.core.util import exception_response_text
from ahriman.models.build_status import BuildStatus, BuildStatusEnum
from ahriman.models.internal_status import InternalStatus
from ahriman.models.package import Package
from ahriman.models.user import User


class WebClient(Client, LazyLogging):
    """
    build status reporter web client

    Attributes:
        address(str): address of the web service
        suppress_errors(bool): suppress logging errors (e.g. if no web server available)
        user(User | None): web service user descriptor
    """

    def __init__(self, configuration: Configuration) -> None:
        """
        default constructor

        Args:
            configuration(Configuration): configuration instance
        """
        self.address, use_unix_socket = self.parse_address(configuration)
        self.user = User.from_option(
            configuration.get("web", "username", fallback=None),
            configuration.get("web", "password", fallback=None))
        self.suppress_errors = configuration.getboolean("settings", "suppress_http_log_errors", fallback=False)

        self.__session = self._create_session(use_unix_socket=use_unix_socket)

    @property
    def _login_url(self) -> str:
        """
        get url for the login api

        Returns:
            str: full url for web service to log in
        """
        return f"{self.address}/api/v1/login"

    @property
    def _status_url(self) -> str:
        """
        get url for the status api

        Returns:
            str: full url for web service for status
        """
        return f"{self.address}/api/v1/status"

    @staticmethod
    def parse_address(configuration: Configuration) -> tuple[str, bool]:
        """
        parse address from configuration

        Args:
            configuration(Configuration): configuration instance

        Returns:
            tuple[str, bool]: tuple of server address and socket flag (True in case if unix socket must be used)
        """
        if (unix_socket := configuration.get("web", "unix_socket", fallback=None)) is not None:
            # special pseudo-protocol which is used for unix sockets
            return f"http+unix://{urlencode(unix_socket)}", True
        address = configuration.get("web", "address", fallback=None)
        if not address:
            # build address from host and port directly
            host = configuration.get("web", "host")
            port = configuration.getint("web", "port")
            address = f"http://{host}:{port}"
        return address, False

    @contextlib.contextmanager
    def __get_session(self, session: requests.Session | None = None) -> Generator[requests.Session, None, None]:
        """
        execute request and handle exceptions

        Args:
            session(requests.Session | None, optional): session to be used or stored instance property otherwise
                (Default value = None)

        Yields:
            requests.Session: session for requests
        """
        try:
            if session is not None:
                yield session  # use session from arguments
            else:
                yield self.__session  # use instance generated session
        except requests.RequestException as e:
            if self.suppress_errors:
                return
            self.logger.exception("could not perform http request: %s", exception_response_text(e))
        except Exception:
            if self.suppress_errors:
                return
            self.logger.exception("could not perform http request")

    def _create_session(self, *, use_unix_socket: bool) -> requests.Session:
        """
        generate new request session

        Args:
            use_unix_socket(bool): if set to True then unix socket session will be generated instead of native requests

        Returns:
            requests.Session: generated session object
        """
        if use_unix_socket:
            import requests_unixsocket  # type: ignore[import]
            session: requests.Session = requests_unixsocket.Session()
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
        if self.user is None:
            return  # no auth configured

        payload = {
            "username": self.user.username,
            "password": self.user.password
        }
        self.make_request("POST", self._login_url, json=payload, session=session)

    def _logs_url(self, package_base: str) -> str:
        """
        get url for the logs api

        Args:
            package_base(str): package base

        Returns:
            str: full url for web service for logs
        """
        return f"{self.address}/api/v1/packages/{package_base}/logs"

    def _package_url(self, package_base: str = "") -> str:
        """
        url generator

        Args:
            package_base(str, optional): package base to generate url (Default value = "")

        Returns:
            str: full url of web service for specific package base
        """
        # in case if unix socket is used we need to normalize url
        suffix = f"/{package_base}" if package_base else ""
        return f"{self.address}/api/v1/packages{suffix}"

    def make_request(self, method: Literal["DELETE", "GET", "POST"], url: str,
                     params: list[tuple[str, str]] | None = None, json: dict[str, Any] | None = None,
                     session: requests.Session | None = None) -> requests.Response | None:
        """
        perform request with specified parameters

        Args:
            method(Literal["DELETE", "GET", "POST"]): HTTP method to call
            url(str): remote url to call
            params(list[tuple[str, str]] | None, optional): request query parameters (Default value = None)
            json(dict[str, Any] | None, optional): request json parameters (Default value = None)
            session(requests.Session | None, optional): session object if any (Default value = None)

        Returns:
            requests.Response | None: response object or None in case of errors
        """
        with self.__get_session(session) as _session:
            response = _session.request(method, url, params=params, json=json)
            response.raise_for_status()
            return response

        # noinspection PyUnreachableCode
        return None

    def package_add(self, package: Package, status: BuildStatusEnum) -> None:
        """
        add new package with status

        Args:
            package(Package): package properties
            status(BuildStatusEnum): current package build status
        """
        payload = {
            "status": status.value,
            "package": package.view()
        }
        self.make_request("POST", self._package_url(package.base), json=payload)

    def package_get(self, package_base: str | None) -> list[tuple[Package, BuildStatus]]:
        """
        get package status

        Args:
            package_base(str | None): package base to get

        Returns:
            list[tuple[Package, BuildStatus]]: list of current package description and status if it has been found
        """
        response = self.make_request("GET", self._package_url(package_base or ""))
        if response is None:
            return []

        response_json = response.json()
        return [
            (Package.from_json(package["package"]), BuildStatus.from_json(package["status"]))
            for package in response_json
        ]

    def package_logs(self, package_base: str, record: logging.LogRecord) -> None:
        """
        post log record

        Args:
            package_base(str) package base
            record(logging.LogRecord): log record to post to api
        """
        payload = {
            "created": record.created,
            "message": record.getMessage(),
            "process_id": record.process,
        }
        self.make_request("POST", self._logs_url(package_base), json=payload)

    def package_remove(self, package_base: str) -> None:
        """
        remove packages from watcher

        Args:
            package_base(str): basename to remove
        """
        self.make_request("DELETE", self._package_url(package_base))

    def package_update(self, package_base: str, status: BuildStatusEnum) -> None:
        """
        update package build status. Unlike ``add`` it does not update package properties

        Args:
            package_base(str): package base to update
            status(BuildStatusEnum): current package build status
        """
        payload = {"status": status.value}
        self.make_request("POST", self._package_url(package_base), json=payload)

    def status_get(self) -> InternalStatus:
        """
        get internal service status

        Returns:
            InternalStatus: current internal (web) service status
        """
        response = self.make_request("GET", self._status_url)
        if response is None:
            return InternalStatus(status=BuildStatus())

        response_json = response.json()
        return InternalStatus.from_json(response_json)

    def status_update(self, status: BuildStatusEnum) -> None:
        """
        update ahriman status itself

        Args:
            status(BuildStatusEnum): current ahriman status
        """
        payload = {"status": status.value}
        self.make_request("POST", self._status_url, json=payload)
