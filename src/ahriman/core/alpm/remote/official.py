#
# Copyright (c) 2021-2024 ahriman team.
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
from typing import Any

from ahriman.core.alpm.pacman import Pacman
from ahriman.core.alpm.remote.remote import Remote
from ahriman.core.exceptions import PackageInfoError, UnknownPackageError
from ahriman.models.aur_package import AURPackage


class Official(Remote):
    """
    official repository RPC wrapper

    Attributes:
        DEFAULT_ARCHLINUX_URL(str): (class attribute) default archlinux url
        DEFAULT_ARCHLINUX_GIT_URL(str): (class attribute) default url for git packages
        DEFAULT_SEARCH_REPOSITORIES(list[str]): (class attribute) default list of repositories to search
        DEFAULT_RPC_URL(str): (class attribute) default archlinux repositories RPC url
    """

    DEFAULT_ARCHLINUX_GIT_URL = "https://gitlab.archlinux.org"
    DEFAULT_ARCHLINUX_URL = "https://archlinux.org"
    DEFAULT_SEARCH_REPOSITORIES = ["Core", "Extra", "Multilib"]
    DEFAULT_RPC_URL = "https://archlinux.org/packages/search/json"

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
        return f"{Official.DEFAULT_ARCHLINUX_GIT_URL}/archlinux/packaging/packages/{package_base}.git"

    @classmethod
    def remote_web_url(cls, package_base: str) -> str:
        """
        generate remote web url from the package base

        Args
            package_base(str): package base

        Returns:
            str: web url for the specific base
        """
        return f"{Official.DEFAULT_ARCHLINUX_URL}/packages/{package_base}"

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
        if not response["valid"]:
            raise PackageInfoError("API validation error")
        return [AURPackage.from_repo(package) for package in response["results"]]

    def arch_request(self, *args: str, by: str) -> list[AURPackage]:
        """
        perform request to official repositories RPC

        Args:
            *args(str): list of arguments to be passed as args query parameter
            by(str): search by the field

        Returns:
            list[AURPackage]: response parsed to package list
        """
        query: list[tuple[str, str]] = [
            ("repo", repository)
            for repository in self.DEFAULT_SEARCH_REPOSITORIES
        ]
        for arg in args:
            query.append((by, arg))

        response = self.make_request("GET", self.DEFAULT_RPC_URL, params=query)
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
        packages = self.arch_request(package_name, by="name")
        try:
            return next(package for package in packages if package.name == package_name)
        except StopIteration:
            raise UnknownPackageError(package_name) from None

    def package_search(self, *keywords: str, pacman: Pacman | None) -> list[AURPackage]:
        """
        search package in AUR web

        Args:
            *keywords(str): keywords to search
            pacman(Pacman | None): alpm wrapper instance, required for official repositories search

        Returns:
            list[AURPackage]: list of packages which match the criteria
        """
        return self.arch_request(*keywords, by="q")
