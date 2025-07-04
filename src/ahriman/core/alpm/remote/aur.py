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
from typing import Any, ClassVar

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.alpm.remote.remote import Remote
from ahriman.core.exceptions import PackageInfoError, UnknownPackageError
from ahriman.models.aur_package import AURPackage


class AUR(Remote):
    """
    AUR RPC wrapper

    Attributes:
        DEFAULT_AUR_URL(str): (class attribute) default AUR url
        DEFAULT_RPC_URL(str): (class attribute) default AUR RPC url
        DEFAULT_RPC_VERSION(str): (class attribute) default AUR RPC version
    """

    DEFAULT_AUR_URL: ClassVar[str] = "https://aur.archlinux.org"
    DEFAULT_RPC_URL: ClassVar[str] = f"{DEFAULT_AUR_URL}/rpc"
    DEFAULT_RPC_VERSION: ClassVar[str] = "5"

    @classmethod
    def remote_git_url(cls, package_base: str, repository: str) -> str:
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
    def remote_web_url(cls, package_base: str) -> str:
        """
        generate remote web url from the package base

        Args
            package_base(str): package base

        Returns:
            str: web url for the specific base
        """
        return f"{AUR.DEFAULT_AUR_URL}/packages/{package_base}"

    @staticmethod
    def parse_response(response: dict[str, Any]) -> list[AURPackage]:
        """
        parse RPC response to package list

        Args:
            response(dict[str, Any]): RPC response json

        Returns:
            list[AURPackage]: list of parsed packages

        Raises:
            PackageInfoError: for error API response
        """
        response_type = response["type"]
        if response_type == "error":
            error_details = response.get("error", "Unknown API error")
            raise PackageInfoError(error_details)
        return [AURPackage.from_json(package) for package in response["results"]]

    def aur_request(self, request_type: str, *args: str, **kwargs: str) -> list[AURPackage]:
        """
        perform request to AUR RPC

        Args:
            request_type(str): AUR request type, e.g. search, info
            *args(str): list of arguments to be passed as args query parameter
            **kwargs(str): list of additional named parameters like by

        Returns:
            list[AURPackage]: response parsed to package list

        Raises:
            PackageInfoError: if multiple arguments are passed
        """
        if len(args) != 1:
            raise PackageInfoError("AUR API requires exactly one argument to search")

        url = f"{self.DEFAULT_RPC_URL}/v{self.DEFAULT_RPC_VERSION}/{request_type}/{args[0]}"
        query = list(kwargs.items())

        response = self.make_request("GET", url, params=query)
        return self.parse_response(response.json())

    def package_info(self, package_name: str, *, pacman: Pacman | None) -> AURPackage:
        """
        get package info by its name

        Args:
            package_name(str): package name to search
            pacman(Pacman | None): alpm wrapper instance, required for official repositories search

        Returns:
            AURPackage: package which match the package name

        Raises:
            UnknownPackageError: package doesn't exist
        """
        packages = self.aur_request("info", package_name)
        try:
            return next(package for package in packages if package.name == package_name)
        except StopIteration:
            raise UnknownPackageError(package_name) from None

    def package_provided_by(self, package_name: str, *, pacman: Pacman | None) -> list[AURPackage]:
        """
        get package list which provide the specified package name

        Args:
            package_name(str): package name to search
            pacman(Pacman | None): alpm wrapper instance, required for official repositories search

        Returns:
            list[AURPackage]: list of packages which match the criteria
        """
        return [
            package
            # search api provides reduced models
            for stub in self.package_search(package_name, pacman=pacman, search_by="provides")
            # verity that found package actually provides it
            if package_name in (package := self.package_info(stub.package_base, pacman=pacman)).provides
        ]

    def package_search(self, *keywords: str, pacman: Pacman | None, search_by: str | None) -> list[AURPackage]:
        """
        search package in AUR web

        Args:
            *keywords(str): keywords to search
            pacman(Pacman | None): alpm wrapper instance, required for official repositories search
            search_by(str | None): search by keywords

        Returns:
            list[AURPackage]: list of packages which match the criteria
        """
        search_by = search_by or "name-desc"
        return self.aur_request("search", *keywords, by=search_by)
