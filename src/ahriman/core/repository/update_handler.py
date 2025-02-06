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
from collections.abc import Iterable

from ahriman.core.build_tools.sources import Sources
from ahriman.core.exceptions import UnknownPackageError
from ahriman.core.repository.cleaner import Cleaner
from ahriman.core.repository.package_info import PackageInfo
from ahriman.models.event import EventType
from ahriman.models.package import Package
from ahriman.models.package_source import PackageSource
from ahriman.models.remote_source import RemoteSource


class UpdateHandler(PackageInfo, Cleaner):
    """
    trait to get package update list
    """

    def updates_aur(self, filter_packages: Iterable[str], *, vcs: bool) -> list[Package]:
        """
        check AUR for updates

        Args:
            filter_packages(Iterable[str]): do not check every package just specified in the list
            vcs(bool): enable or disable checking of VCS packages

        Returns:
            list[Package]: list of packages which are out-of-dated
        """
        def load_remote(package: Package) -> Package:
            # try to load package from base and if none found try to load by separated packages
            for probe in [package.base] + sorted(package.packages.keys()):
                try:
                    if package.remote.source == PackageSource.Repository:
                        return Package.from_official(probe, self.pacman, None)
                    return Package.from_aur(probe, None)
                except UnknownPackageError:
                    continue
            raise UnknownPackageError(package.base)

        result: list[Package] = []
        for local in self.packages(filter_packages):
            with self.in_package_context(local.base, local.version):
                if not local.remote.is_remote:
                    continue  # avoid checking local packages
                if local.base in self.ignore_list:
                    continue

                try:
                    remote = load_remote(local)

                    if local.is_outdated(remote, self.configuration, calculate_version=vcs):
                        self.reporter.set_pending(local.base)
                        self.event(local.base, EventType.PackageOutdated, "Remote version is newer than local")
                        result.append(remote)
                except Exception:
                    self.reporter.set_failed(local.base)
                    self.logger.exception("could not load remote package %s", local.base)

        return result

    def updates_dependencies(self, filter_packages: Iterable[str]) -> list[Package]:
        """
        check packages which ae required to be rebuilt based on dynamic dependencies (e.g. linking, modules paths, etc.)

        Args:
            filter_packages(Iterable[str]): do not check every package just specified in the list

        Returns:
            list[Package]: list of packages for which there is breaking linking
        """
        def extract_files(lookup_packages: Iterable[str]) -> dict[str, set[str]]:
            database_files = self.pacman.files(lookup_packages)
            files: dict[str, set[str]] = {}
            for package_name, package_files in database_files.items():  # invert map
                for package_file in package_files:
                    files.setdefault(package_file, set()).add(package_name)

            return files

        result: list[Package] = []
        for local in self.packages(filter_packages):
            dependencies = self.reporter.package_dependencies_get(local.base)
            if not dependencies.paths:
                continue  # skip check if no package dependencies found

            required_packages = {dep for dep_packages in dependencies.paths.values() for dep in dep_packages}
            filesystem = extract_files(required_packages)

            for path, packages in dependencies.paths.items():
                found = filesystem.get(path, set())
                if found.intersection(packages):
                    continue

                # there are no packages found in filesystem with the same paths
                self.reporter.set_pending(local.base)
                self.event(local.base, EventType.PackageOutdated, "Implicit dependencies are broken")
                result.append(local)

                break

        return result

    def updates_local(self, *, vcs: bool) -> list[Package]:
        """
        check local packages for updates

        Args:
            vcs(bool): enable or disable checking of VCS packages

        Returns:
            list[Package]: list of local packages which are out-of-dated
        """
        packages = {local.base: local for local in self.packages()}
        local_versions = {package_base: package.version for package_base, package in packages.items()}

        result: list[Package] = []
        for cache_dir in self.paths.cache.iterdir():
            with self.in_package_context(cache_dir.name, local_versions.get(cache_dir.name)):
                try:
                    source = RemoteSource(
                        source=PackageSource.Local,
                        git_url=cache_dir.absolute().as_uri(),
                        web_url="",
                        path=".",
                        branch="master",
                    )

                    Sources.fetch(cache_dir, source)
                    remote = Package.from_build(cache_dir, self.architecture, None)

                    local = packages.get(remote.base)
                    if local is None:
                        continue  # we don't add packages automatically
                    if local.remote.is_remote:
                        continue  # avoid checking AUR packages

                    if local.is_outdated(remote, self.configuration, calculate_version=vcs):
                        self.reporter.set_pending(local.base)
                        self.event(local.base, EventType.PackageOutdated, "Locally pulled sources are outdated")
                        result.append(remote)
                except Exception:
                    self.logger.exception("could not process package at %s", cache_dir)

        return result

    def updates_manual(self) -> list[Package]:
        """
        check for packages for which manual update has been requested

        Returns:
            list[Package]: list of packages which are out-of-dated
        """
        result: list[Package] = []
        known_bases = {package.base for package in self.packages()}

        try:
            for local in self.database.build_queue_get():
                result.append(local)
                if local.base not in known_bases:
                    self.reporter.set_unknown(local)
                else:
                    self.reporter.set_pending(local.base)
                self.event(local.base, EventType.PackageOutdated, "Manual update is requested")
        except Exception:
            self.logger.exception("could not load packages from database")
        self.clear_queue()

        return result
