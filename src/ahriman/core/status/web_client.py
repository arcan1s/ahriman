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
import logging
import requests

from typing import List, Optional, Tuple

from ahriman.core.status.client import Client
from ahriman.models.build_status import BuildStatusEnum, BuildStatus
from ahriman.models.package import Package


class WebClient(Client):
    """
    build status reporter web client
    :ivar host: host of web service
    :ivar logger: class logger
    :ivar port: port of web service
    """

    def __init__(self, host: str, port: int) -> None:
        """
        default constructor
        :param host: host of web service
        :param port: port of web service
        """
        self.logger = logging.getLogger("http")
        self.host = host
        self.port = port

    @staticmethod
    def _exception_response_text(exception: requests.exceptions.HTTPError) -> str:
        """
        safe response exception text generation
        :param exception: exception raised
        :return: text of the response if it is not None and empty string otherwise
        """
        return exception.response.text if exception.response is not None else ''

    def _ahriman_url(self) -> str:
        """
        url generator
        :return: full url for web service for ahriman service itself
        """
        return f"http://{self.host}:{self.port}/api/v1/ahriman"

    def _package_url(self, base: str = "") -> str:
        """
        url generator
        :param base: package base to generate url
        :return: full url of web service for specific package base
        """
        return f"http://{self.host}:{self.port}/api/v1/packages/{base}"

    def add(self, package: Package, status: BuildStatusEnum) -> None:
        """
        add new package with status
        :param package: package properties
        :param status: current package build status
        """
        payload = {
            "status": status.value,
            "package": package.view()
        }

        try:
            response = requests.post(self._package_url(package.base), json=payload)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self.logger.exception(f"could not add {package.base}: {WebClient._exception_response_text(e)}")
        except Exception:
            self.logger.exception(f"could not add {package.base}")

    def get(self, base: Optional[str]) -> List[Tuple[Package, BuildStatus]]:
        """
        get package status
        :param base: package base to get
        :return: list of current package description and status if it has been found
        """
        try:
            response = requests.get(self._package_url(base or ""))
            response.raise_for_status()

            status_json = response.json()
            return [
                (Package.from_json(package["package"]), BuildStatus.from_json(package["status"]))
                for package in status_json
            ]
        except requests.exceptions.HTTPError as e:
            self.logger.exception(f"could not get {base}: {WebClient._exception_response_text(e)}")
        except Exception:
            self.logger.exception(f"could not get {base}")
        return []

    def get_self(self) -> BuildStatus:
        """
        get ahriman status itself
        :return: current ahriman status
        """
        try:
            response = requests.get(self._ahriman_url())
            response.raise_for_status()

            status_json = response.json()
            return BuildStatus.from_json(status_json)
        except requests.exceptions.HTTPError as e:
            self.logger.exception(f"could not get service status: {WebClient._exception_response_text(e)}")
        except Exception:
            self.logger.exception("could not get service status")
        return BuildStatus()

    def remove(self, base: str) -> None:
        """
        remove packages from watcher
        :param base: basename to remove
        """
        try:
            response = requests.delete(self._package_url(base))
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self.logger.exception(f"could not delete {base}: {WebClient._exception_response_text(e)}")
        except Exception:
            self.logger.exception(f"could not delete {base}")

    def update(self, base: str, status: BuildStatusEnum) -> None:
        """
        update package build status. Unlike `add` it does not update package properties
        :param base: package base to update
        :param status: current package build status
        """
        payload = {"status": status.value}

        try:
            response = requests.post(self._package_url(base), json=payload)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self.logger.exception(f"could not update {base}: {WebClient._exception_response_text(e)}")
        except Exception:
            self.logger.exception(f"could not update {base}")

    def update_self(self, status: BuildStatusEnum) -> None:
        """
        update ahriman status itself
        :param status: current ahriman status
        """
        payload = {"status": status.value}

        try:
            response = requests.post(self._ahriman_url(), json=payload)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self.logger.exception(f"could not update service status: {WebClient._exception_response_text(e)}")
        except Exception:
            self.logger.exception("could not update service status")
