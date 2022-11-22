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
import logging
import requests

from typing import List, Optional, Tuple

from ahriman.core.configuration import Configuration
from ahriman.core.log import LazyLogging
from ahriman.core.status.client import Client
from ahriman.core.util import exception_response_text
from ahriman.models.build_status import BuildStatusEnum, BuildStatus
from ahriman.models.internal_status import InternalStatus
from ahriman.models.package import Package
from ahriman.models.user import User


class WebClient(Client, LazyLogging):
    """
    build status reporter web client

    Attributes:
        address(str): address of the web service
        user(Optional[User]): web service user descriptor
    """

    def __init__(self, configuration: Configuration) -> None:
        """
        default constructor

        Args:
            configuration(Configuration): configuration instance
        """
        self.address = self.parse_address(configuration)
        self.user = User.from_option(
            configuration.get("web", "username", fallback=None),
            configuration.get("web", "password", fallback=None))

        self.__session = requests.session()
        self._login()

    @property
    def _login_url(self) -> str:
        """
        get url for the login api

        Returns:
            str: full url for web service to login
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
    def parse_address(configuration: Configuration) -> str:
        """
        parse address from configuration

        Args:
            configuration(Configuration): configuration instance

        Returns:
            str: valid http address
        """
        address = configuration.get("web", "address", fallback=None)
        if not address:
            # build address from host and port directly
            host = configuration.get("web", "host")
            port = configuration.getint("web", "port")
            address = f"http://{host}:{port}"
        return address

    def _login(self) -> None:
        """
        process login to the service
        """
        if self.user is None:
            return  # no auth configured

        payload = {
            "username": self.user.username,
            "password": self.user.password
        }

        try:
            response = self.__session.post(self._login_url, json=payload)
            response.raise_for_status()
        except requests.HTTPError as e:
            self.logger.exception("could not login as %s: %s", self.user, exception_response_text(e))
        except Exception:
            self.logger.exception("could not login as %s", self.user)

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
        return f"{self.address}/api/v1/packages/{package_base}"

    def add(self, package: Package, status: BuildStatusEnum) -> None:
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

        try:
            response = self.__session.post(self._package_url(package.base), json=payload)
            response.raise_for_status()
        except requests.HTTPError as e:
            self.logger.exception("could not add %s: %s", package.base, exception_response_text(e))
        except Exception:
            self.logger.exception("could not add %s", package.base)

    def get(self, package_base: Optional[str]) -> List[Tuple[Package, BuildStatus]]:
        """
        get package status

        Args:
            package_base(Optional[str]): package base to get

        Returns:
            List[Tuple[Package, BuildStatus]]: list of current package description and status if it has been found
        """
        try:
            response = self.__session.get(self._package_url(package_base or ""))
            response.raise_for_status()

            status_json = response.json()
            return [
                (Package.from_json(package["package"]), BuildStatus.from_json(package["status"]))
                for package in status_json
            ]
        except requests.HTTPError as e:
            self.logger.exception("could not get %s: %s", package_base, exception_response_text(e))
        except Exception:
            self.logger.exception("could not get %s", package_base)
        return []

    def get_internal(self) -> InternalStatus:
        """
        get internal service status

        Returns:
            InternalStatus: current internal (web) service status
        """
        try:
            response = self.__session.get(self._status_url)
            response.raise_for_status()

            status_json = response.json()
            return InternalStatus.from_json(status_json)
        except requests.HTTPError as e:
            self.logger.exception("could not get web service status: %s", exception_response_text(e))
        except Exception:
            self.logger.exception("could not get web service status")
        return InternalStatus(status=BuildStatus())

    def logs(self, package_base: str, record: logging.LogRecord) -> None:
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

        # in this method exception has to be handled outside in logger handler
        response = self.__session.post(self._logs_url(package_base), json=payload)
        response.raise_for_status()

    def remove(self, package_base: str) -> None:
        """
        remove packages from watcher

        Args:
            package_base(str): basename to remove
        """
        try:
            response = self.__session.delete(self._package_url(package_base))
            response.raise_for_status()
        except requests.HTTPError as e:
            self.logger.exception("could not delete %s: %s", package_base, exception_response_text(e))
        except Exception:
            self.logger.exception("could not delete %s", package_base)

    def update(self, package_base: str, status: BuildStatusEnum) -> None:
        """
        update package build status. Unlike ``add`` it does not update package properties

        Args:
            package_base(str): package base to update
            status(BuildStatusEnum): current package build status
        """
        payload = {"status": status.value}

        try:
            response = self.__session.post(self._package_url(package_base), json=payload)
            response.raise_for_status()
        except requests.HTTPError as e:
            self.logger.exception("could not update %s: %s", package_base, exception_response_text(e))
        except Exception:
            self.logger.exception("could not update %s", package_base)

    def update_self(self, status: BuildStatusEnum) -> None:
        """
        update ahriman status itself

        Args:
            status(BuildStatusEnum): current ahriman status
        """
        payload = {"status": status.value}

        try:
            response = self.__session.post(self._status_url, json=payload)
            response.raise_for_status()
        except requests.HTTPError as e:
            self.logger.exception("could not update service status: %s", exception_response_text(e))
        except Exception:
            self.logger.exception("could not update service status")
