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
import requests

from typing import Any, Dict, List, Type

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.alpm.remote import Remote
from ahriman.core.exceptions import InvalidPackageInfo
from ahriman.core.util import exception_response_text
from ahriman.models.aur_package import AURPackage


class AUR(Remote):
    """
    AUR RPC wrapper

    Attributes:
        DEFAULT_AUR_URL(str): (class attribute) default AUR url
        DEFAULT_RPC_URL(str): (class attribute) default AUR RPC url
        DEFAULT_RPC_VERSION(str): (class attribute) default AUR RPC version
    """

    DEFAULT_AUR_URL = "https://aur.archlinux.org"
    DEFAULT_RPC_URL = f"{DEFAULT_AUR_URL}/rpc"
    DEFAULT_RPC_VERSION = "5"

    @staticmethod
    def parse_response(response: Dict[str, Any]) -> List[AURPackage]:
        """
        parse RPC response to package list

        Args:
            response(Dict[str, Any]): RPC response json

        Returns:
            List[AURPackage]: list of parsed packages

        Raises:
            InvalidPackageInfo: for error API response
        """
        response_type = response["type"]
        if response_type == "error":
            error_details = response.get("error", "Unknown API error")
            raise InvalidPackageInfo(error_details)
        return [AURPackage.from_json(package) for package in response["results"]]

    @classmethod
    def remote_git_url(cls: Type[Remote], package_base: str, repository: str) -> str:
        """
        generate remote git url from the package base

        Args
            package_base(str): package base
            repository(str): repository name

        Returns:
            str: git url for the specific base
        """
        return f"{AUR.DEFAULT_AUR_URL}/{package_base}.git"

    @classmethod
    def remote_web_url(cls: Type[Remote], package_base: str) -> str:
        """
        generate remote web url from the package base

        Args
            package_base(str): package base

        Returns:
            str: web url for the specific base
        """
        return f"{AUR.DEFAULT_AUR_URL}/packages/{package_base}"

    def make_request(self, request_type: str, *args: str, **kwargs: str) -> List[AURPackage]:
        """
        perform request to AUR RPC

        Args:
            request_type(str): AUR request type, e.g. search, info
            *args(str): list of arguments to be passed as args query parameter
            **kwargs(str): list of additional named parameters like by

        Returns:
            List[AURPackage]: response parsed to package list
        """
        query: Dict[str, Any] = {
            "type": request_type,
            "v": self.DEFAULT_RPC_VERSION
        }

        arg_query = "arg[]" if len(args) > 1 else "arg"
        query[arg_query] = list(args)

        for key, value in kwargs.items():
            query[key] = value

        try:
            response = requests.get(self.DEFAULT_RPC_URL, params=query)
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

    def package_info(self, package_name: str, *, pacman: Pacman) -> AURPackage:
        """
        get package info by its name

        Args:
            package_name(str): package name to search
            pacman(Pacman): alpm wrapper instance

        Returns:
            AURPackage: package which match the package name
        """
        packages = self.make_request("info", package_name)
        return next(package for package in packages if package.name == package_name)

    def package_search(self, *keywords: str, pacman: Pacman) -> List[AURPackage]:
        """
        search package in AUR web

        Args:
            *keywords(str): keywords to search
            pacman(Pacman): alpm wrapper instance

        Returns:
            List[AURPackage]: list of packages which match the criteria
        """
        return self.make_request("search", *keywords, by="name-desc")
