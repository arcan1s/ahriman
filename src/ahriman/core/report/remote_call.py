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

from ahriman.core.configuration import Configuration
from ahriman.core.report.report import Report
from ahriman.core.status.web_client import WebClient
from ahriman.models.package import Package
from ahriman.models.result import Result
from ahriman.models.waiter import Waiter


class RemoteCall(Report):
    """
    trigger implementation which call remote service with update

    Attributes:
        client(WebClient): web client instance
        update_aur(bool): check for AUR updates
        update_local(bool): check for local packages update
        update_manual(bool): check for manually built packages
        wait_timeout(int): timeout to wait external process
    """

    def __init__(self, architecture: str, configuration: Configuration, section: str) -> None:
        """
        default constructor

        Args:
            architecture(str): repository architecture
            configuration(Configuration): configuration instance
            section(str): settings section name
        """
        Report.__init__(self, architecture, configuration)

        self.client = WebClient(configuration)

        self.update_aur = configuration.getboolean(section, "aur", fallback=False)
        self.update_local = configuration.getboolean(section, "local", fallback=False)
        self.update_manual = configuration.getboolean(section, "manual", fallback=False)

        self.wait_timeout = configuration.getint(section, "wait_timeout", fallback=-1)

    def generate(self, packages: list[Package], result: Result) -> None:
        """
        generate report for the specified packages

        Args:
            packages(list[Package]): list of packages to generate report
            result(Result): build result
        """
        process_id = self.remote_update()
        self.remote_wait(process_id)

    def is_process_alive(self, process_id: str) -> bool:
        """
        check if process is alive

        Args:
            process_id(str): remote process id

        Returns:
            bool: True in case if remote process is alive and False otherwise
        """
        try:
            response = self.client.make_request("GET", f"/api/v1/service/process/{process_id}")
        except requests.HTTPError as ex:
            status_code = ex.response.status_code if ex.response is not None else None
            if status_code == 404:
                return False
            raise

        response_json = response.json()
        is_alive: bool = response_json["is_alive"]

        return is_alive

    def remote_update(self) -> str:
        """
        call remote server for update

        Returns:
            str: remote process id
        """
        response = self.client.make_request("POST", "/api/v1/service/update", json={
            "aur": self.update_aur,
            "local": self.update_local,
            "manual": self.update_manual,
        })
        response_json = response.json()

        process_id: str = response_json["process_id"]
        return process_id

    def remote_wait(self, process_id: str) -> None:
        """
        wait for remote process termination

        Args:
            process_id(str): remote process id
        """
        waiter = Waiter(self.wait_timeout)
        waiter.wait(self.is_process_alive, process_id)
