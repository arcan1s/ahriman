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
from ahriman.core.alpm.pacman import Pacman
from ahriman.core.exceptions import UnknownPackageError
from ahriman.core.http import SyncHttpClient
from ahriman.models.aur_package import AURPackage


class Remote(SyncHttpClient):
    """
    base class for remote package search

    Examples:
        These classes are designed to be used without instancing. In order to achieve it several class methods are
        provided: :func:`info()`, :func:`multisearch()` and :func:`search()`. Thus, the basic flow is the following::

            >>> from ahriman.core.alpm.remote import AUR, Official
            >>>
            >>> package = AUR.info("ahriman")
            >>> search_result = Official.multisearch("pacman", "manager", pacman=pacman)

        Difference between :func:`search()` and :func:`multisearch()` is that :func:`search()` passes all arguments to
        underlying wrapper directly, whereas :func:`multisearch()` splits search one by one and finds intersection
        between search results.
    """

    @classmethod
    def info(cls, package_name: str, *, pacman: Pacman | None = None, include_provides: bool = False) -> AURPackage:
        """
        get package info by its name. If ``include_provides`` is set to ``True``, then, in addition, this method
        will perform search by :attr:`ahriman.models.aur_package.AURPackage.provides` and return first package found.
        Note, however, that in this case some implementation might not provide this method and search result will might
        not be stable

        Args:
            package_name(str): package name to search
            pacman(Pacman | None, optional): alpm wrapper instance, required for official repositories search
                (Default value = None)
            include_provides(bool, optional): search by provides if no exact match found (Default value = False)

        Returns:
            AURPackage: package which match the package name

        Raises:
            UnknownPackageError: if requested package not found
        """
        instance = cls()
        try:
            return instance.package_info(package_name, pacman=pacman)
        except UnknownPackageError:
            if include_provides and (provided_by := instance.package_provided_by(package_name, pacman=pacman)):
                return next(iter(provided_by))
            raise

    @classmethod
    def multisearch(cls, *keywords: str, pacman: Pacman | None = None,
                    search_by: str | None = None) -> list[AURPackage]:
        """
        search in remote repository by using API with multiple words. This method is required in order to handle
        https://bugs.archlinux.org/task/49133. In addition, short words will be dropped

        Args:
            *keywords(str): search terms, e.g. "ahriman", "is", "cool"
            pacman(Pacman | None, optional): alpm wrapper instance, required for official repositories search
                (Default value = None)
            search_by(str | None, optional): search by keywords (Default value = None)

        Returns:
            list[AURPackage]: list of packages each of them matches all search terms
        """
        instance = cls()
        packages: dict[str, AURPackage] = {}
        for term in filter(lambda word: len(word) >= 3, keywords):
            portion = instance.package_search(term, pacman=pacman, search_by=search_by)
            packages = {
                package.name: package  # not mistake to group them by name
                for package in portion
                if package.name in packages or not packages
            }

        # simple check for duplicates. This method will remove all packages under base if there is
        # a package named exactly as its base
        packages = {
            package.name: package
            for package in packages.values()
            if package.package_base not in packages or package.package_base == package.name
        }

        return list(packages.values())

    @classmethod
    def remote_git_url(cls, package_base: str, repository: str) -> str:
        """
        generate remote git url from the package base

        Args
            package_base(str): package base
            repository(str): repository name

        Returns:
            str: git url for the specific base

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    @classmethod
    def remote_web_url(cls, package_base: str) -> str:
        """
        generate remote web url from the package base

        Args
            package_base(str): package base

        Returns:
            str: web url for the specific base

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    @classmethod
    def search(cls, *keywords: str, pacman: Pacman | None = None, search_by: str | None = None) -> list[AURPackage]:
        """
        search package in AUR web

        Args:
            *keywords(str): search terms, e.g. "ahriman", "is", "cool"
            pacman(Pacman | None, optional): alpm wrapper instance, required for official repositories search
                (Default value = None)
            search_by(str | None, optional): search by keywords (Default value = None)

        Returns:
            list[AURPackage]: list of packages which match the criteria
        """
        return cls().package_search(*keywords, pacman=pacman, search_by=search_by)

    def package_info(self, package_name: str, *, pacman: Pacman | None) -> AURPackage:
        """
        get package info by its name

        Args:
            package_name(str): package name to search
            pacman(Pacman | None): alpm wrapper instance, required for official repositories search

        Returns:
            AURPackage: package which match the package name

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

    def package_provided_by(self, package_name: str, *, pacman: Pacman | None) -> list[AURPackage]:
        """
        get package list which provide the specified package name

        Args:
            package_name(str): package name to search
            pacman(Pacman | None): alpm wrapper instance, required for official repositories search

        Returns:
            list[AURPackage]: list of packages which match the criteria
        """
        del package_name, pacman
        return []

    def package_search(self, *keywords: str, pacman: Pacman | None, search_by: str | None) -> list[AURPackage]:
        """
        search package in AUR web

        Args:
            *keywords(str): keywords to search
            pacman(Pacman | None): alpm wrapper instance, required for official repositories search
            search_by(str | None): search by keywords

        Returns:
            list[AURPackage]: list of packages which match the criteria

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError
