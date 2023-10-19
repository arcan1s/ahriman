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
from collections.abc import Iterable

from ahriman.core.build_tools.sources import Sources
from ahriman.core.exceptions import UnknownPackageError
from ahriman.core.repository.cleaner import Cleaner
from ahriman.models.package import Package
from ahriman.models.package_source import PackageSource
from ahriman.models.remote_source import RemoteSource


class UpdateHandler(Cleaner):
    """
    trait to get package update list
    """

    def packages(self) -> list[Package]:
        """
        generate list of repository packages

        Returns:
            list[Package]: list of packages properties

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError

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

        local_versions = {package.base: package.version for package in self.packages()}

        result: list[Package] = []
        for local in self.packages():
            with self.in_package_context(local.base, local_versions.get(local.base)):
                if not local.remote.is_remote:
                    continue  # avoid checking local packages
                if local.base in self.ignore_list:
                    continue
                if filter_packages and local.base not in filter_packages:
                    continue

                try:
                    remote = load_remote(local)

                    if local.is_outdated(
                            remote, self.paths,
                            vcs_allowed_age=self.vcs_allowed_age,
                            calculate_version=vcs):
                        self.reporter.set_pending(local.base)
                        result.append(remote)
                except Exception:
                    self.reporter.set_failed(local.base)
                    self.logger.exception("could not load remote package %s", local.base)

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

                    if local.is_outdated(remote, self.paths,
                                         vcs_allowed_age=self.vcs_allowed_age,
                                         calculate_version=vcs):
                        self.reporter.set_pending(local.base)
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
        except Exception:
            self.logger.exception("could not load packages from database")
        self.clear_queue()

        return result
