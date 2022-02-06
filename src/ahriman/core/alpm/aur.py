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
from __future__ import annotations

import logging
import requests

from typing import Any, Dict, List, Optional, Type

from ahriman.core.exceptions import InvalidPackageInfo
from ahriman.core.util import exception_response_text
from ahriman.models.aur_package import AURPackage


class AUR:
    """
    AUR RPC wrapper
    :cvar DEFAULT_RPC_URL: default AUR RPC url
    :cvar DEFAULT_RPC_VERSION: default AUR RPC version
    :ivar logger: class logger
    :ivar rpc_url: AUR RPC url
    :ivar rpc_version: AUR RPC version
    """

    DEFAULT_RPC_URL = "https://aur.archlinux.org/rpc"
    DEFAULT_RPC_VERSION = "5"

    def __init__(self, rpc_url: Optional[str] = None, rpc_version: Optional[str] = None) -> None:
        """
        default constructor
        :param rpc_url: AUR RPC url
        :param rpc_version: AUR RPC version
        """
        self.rpc_url = rpc_url or self.DEFAULT_RPC_URL
        self.rpc_version = rpc_version or self.DEFAULT_RPC_VERSION
        self.logger = logging.getLogger("build_details")

    @classmethod
    def info(cls: Type[AUR], package_name: str) -> AURPackage:
        """
        get package info by its name
        :param package_name: package name to search
        :return: package which match the package name
        """
        return cls().package_info(package_name)

    @classmethod
    def multisearch(cls: Type[AUR], *keywords: str) -> List[AURPackage]:
        """
        search in AUR by using API with multiple words. This method is required in order to handle
        https://bugs.archlinux.org/task/49133. In addition short words will be dropped
        :param keywords: search terms, e.g. "ahriman", "is", "cool"
        :return: list of packages each of them matches all search terms
        """
        instance = cls()
        packages: Dict[str, AURPackage] = {}
        for term in filter(lambda word: len(word) > 3, keywords):
            portion = instance.search(term)
            packages = {
                package.package_base: package
                for package in portion
                if package.package_base in packages or not packages
            }
        return list(packages.values())

    @classmethod
    def search(cls: Type[AUR], *keywords: str) -> List[AURPackage]:
        """
        search package in AUR web
        :param keywords: keywords to search
        :return: list of packages which match the criteria
        """
        return cls().package_search(*keywords)

    @staticmethod
    def parse_response(response: Dict[str, Any]) -> List[AURPackage]:
        """
        parse RPC response to package list
        :param response: RPC response json
        :return: list of parsed packages
        """
        response_type = response["type"]
        if response_type == "error":
            error_details = response.get("error", "Unknown API error")
            raise InvalidPackageInfo(error_details)
        return [AURPackage.from_json(package) for package in response["results"]]

    def make_request(self, request_type: str, *args: str, **kwargs: str) -> List[AURPackage]:
        """
        perform request to AUR RPC
        :param request_type: AUR request type, e.g. search, info
        :param args: list of arguments to be passed as args query parameter
        :param kwargs: list of additional named parameters like by
        :return: response parsed to package list
        """
        query: Dict[str, Any] = {
            "type": request_type,
            "v": self.rpc_version
        }

        arg_query = "arg[]" if len(args) > 1 else "arg"
        query[arg_query] = list(args)

        for key, value in kwargs.items():
            query[key] = value

        try:
            response = requests.get(self.rpc_url, params=query)
            response.raise_for_status()
            return self.parse_response(response.json())
        except requests.HTTPError as e:
            self.logger.exception(
                "could not perform request by using type %s: %s",
                request_type,
                exception_response_text(e))
            raise
        except Exception:
            self.logger.exception("could not perform request by using type %s", request_type)
            raise

    def package_info(self, package_name: str) -> AURPackage:
        """
        get package info by its name
        :param package_name: package name to search
        :return: package which match the package name
        """
        packages = self.make_request("info", package_name)
        return next(package for package in packages if package.name == package_name)

    def package_search(self, *keywords: str, by: str = "name-desc") -> List[AURPackage]:
        """
        search package in AUR web
        :param keywords: keywords to search
        :param by: search by the field
        :return: list of packages which match the criteria
        """
        return self.make_request("search", *keywords, by=by)
