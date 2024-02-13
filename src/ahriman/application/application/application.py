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
from collections.abc import Callable, Iterable

from ahriman.application.application.application_packages import ApplicationPackages
from ahriman.application.application.application_repository import ApplicationRepository
from ahriman.core.formatters import UpdatePrinter
from ahriman.core.tree import Tree
from ahriman.models.package import Package
from ahriman.models.result import Result


class Application(ApplicationPackages, ApplicationRepository):
    """
    base application class

    Examples:
        This class groups :class:`ahriman.core.repository.repository.Repository` methods into specific method which
        process all supposed actions caused by underlying action. E.g.::

            >>> from ahriman.core.configuration import Configuration
            >>> from ahriman.models.package_source import PackageSource
            >>> from ahriman.models.repository_id import RepositoryId
            >>>
            >>> configuration = Configuration()
            >>> application = Application(RepositoryId("x86_64", "x86_64"), configuration, report=True)
            >>> # add packages to build queue
            >>> application.add(["ahriman"], PackageSource.AUR)
            >>>
            >>> # check for updates
            >>> updates = application.updates([], aur=True, local=True, manual=True, vcs=True)
            >>> # updates for specified packages
            >>> application.update(updates)

        In case if specific actions or their order are required, the direct access to
        :class:`ahriman.core.repository.repository.Repository` must be used instead.
    """

    def _known_packages(self) -> set[str]:
        """
        load packages from repository and pacman repositories

        Returns:
            set[str]: list of known packages
        """
        known_packages: set[str] = set()
        # local set
        # this action is not really needed in case if ``alpm.use_ahriman_cache`` set to yes, because pacman
        # will eventually contain all the local packages
        for base in self.repository.packages():
            for package, properties in base.packages.items():
                known_packages.add(package)
                known_packages.update(properties.provides)
        # known pacman databases
        known_packages.update(self.repository.pacman.packages())
        return known_packages

    def on_result(self, result: Result) -> None:
        """
        generate report and sync to remote server

        Args:
            result(Result): build result
        """
        packages = self.repository.packages()
        self.repository.triggers.on_result(result, packages)

    def on_start(self) -> None:
        """
        run triggers on start of the application
        """
        self.repository.triggers.on_start()

    def on_stop(self) -> None:
        """
        run triggers on stop of the application. Note, however, that in most cases this method should not be called
        directly as it will be called after on_start action
        """
        self.repository.triggers.on_stop()

    def print_updates(self, packages: list[Package], *, log_fn: Callable[[str], None]) -> None:
        """
        print list of packages to be built. This method will build dependency tree and print updates accordingly

        Args:
            packages(list[Package]): package list to be printed
            log_fn(Callable[[str], None]): logger function to log updates
        """
        local_versions = {package.base: package.version for package in self.repository.packages()}

        tree = Tree.resolve(packages)
        for level in tree:
            for package in level:
                UpdatePrinter(package, local_versions.get(package.base))(verbose=True, log_fn=log_fn, separator=" -> ")

    def with_dependencies(self, packages: list[Package], *, process_dependencies: bool) -> list[Package]:
        """
        add missing dependencies to list of packages. This will extract known packages, check dependencies of
        the supplied packages and add packages which are not presented in the list of known packages.

        Args:
            packages(list[Package]): list of source packages of which dependencies have to be processed
            process_dependencies(bool): if no set, dependencies will not be processed

        Returns:
            list[Package]: updated packages list. Packager for dependencies will be copied from
            original package

        Examples:
            In the most cases, in order to avoid build failure, it is required to add missing packages, which can be
            done by calling::

                >>> application = ...
                >>> packages = application.with_dependencies(packages, process_dependencies=True)
                >>> application.print_updates(packages, log_fn=print)
        """
        def missing_dependencies(source: Iterable[Package]) -> dict[str, str | None]:
            # append list of known packages with packages which are in current sources
            satisfied_packages = known_packages | {
                single
                for package in source
                for single in package.packages_full
            }

            return {
                dependency: package.packager
                for package in source
                for dependency in package.depends_build
                if dependency not in satisfied_packages
            }

        if not process_dependencies or not packages:
            return packages

        known_packages = self._known_packages()
        with_dependencies = {package.base: package for package in packages}

        while missing := missing_dependencies(with_dependencies.values()):
            for package_name, username in missing.items():
                if (source_dir := self.repository.paths.cache_for(package_name)).is_dir():
                    # there is local cache, load package from it
                    package = Package.from_build(source_dir, self.repository.architecture, username)
                else:
                    package = Package.from_aur(package_name, username)
                with_dependencies[package.base] = package

                # register package in local database
                self.database.package_base_update(package)
                self.repository.reporter.set_unknown(package)

        return list(with_dependencies.values())
