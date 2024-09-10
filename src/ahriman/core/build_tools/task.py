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
from collections.abc import Generator
from pathlib import Path

from ahriman.core.build_tools.sources import Sources
from ahriman.core.configuration import Configuration
from ahriman.core.exceptions import BuildError
from ahriman.core.log import LazyLogging
from ahriman.core.utils import check_output, package_like
from ahriman.models.package import Package
from ahriman.models.pkgbuild_patch import PkgbuildPatch
from ahriman.models.repository_paths import RepositoryPaths


class Task(LazyLogging):
    """
    base package build task

    Attributes:
        archbuild_flags(list[str]): command flags for archbuild command
        architecture(str): repository architecture
        build_command(str): build command
        include_debug_packages(bool): whether to include debug packages or not
        makechrootpkg_flags(list[str]): command flags for makechrootpkg command
        makepkg_flags(list[str]): command flags for makepkg command
        package(Package): package definitions
        paths(RepositoryPaths): repository paths instance
        uid(int): uid of the repository owner user
    """

    def __init__(self, package: Package, configuration: Configuration, architecture: str,
                 paths: RepositoryPaths) -> None:
        """
        Args:
            package(Package): package definitions
            configuration(Configuration): configuration instance
            architecture(str): repository architecture
            paths(RepositoryPaths): repository paths instance
        """
        self.package = package
        self.paths = paths
        self.uid, _ = paths.root_owner
        self.architecture = architecture

        self.archbuild_flags = configuration.getlist("build", "archbuild_flags", fallback=[])
        self.build_command = configuration.get("build", "build_command")
        self.include_debug_packages = configuration.getboolean("build", "include_debug_packages", fallback=True)
        self.makepkg_flags = configuration.getlist("build", "makepkg_flags", fallback=[])
        self.makechrootpkg_flags = configuration.getlist("build", "makechrootpkg_flags", fallback=[])

    def _package_archives(self, sources_dir: Path, source_files: list[Path]) -> list[Path]:
        """
        extract package archives from the directory

        Args:
            sources_dir(Path): path to where sources are
            source_files(list[Path]): list of files which were initially in the directory

        Returns:
            list[Path]: list of file paths which looks like freshly generated archives
        """
        def files() -> Generator[Path, None, None]:
            for filepath in sources_dir.iterdir():
                if filepath in source_files:
                    continue  # skip files which were already there
                if filepath.suffix == ".log":
                    continue  # skip log files
                if not package_like(filepath):
                    continue  # path doesn't look like a package
                yield filepath

        # debug packages are always formed as package.base-debug
        # see /usr/share/makepkg/util/pkgbuild.sh for more details
        debug_package_prefix = f"{self.package.base}-debug-"
        return [
            package
            for package in files()
            if self.include_debug_packages or not package.name.startswith(debug_package_prefix)
        ]

    def build(self, sources_dir: Path, **kwargs: str | None) -> list[Path]:
        """
        run package build

        Args:
            sources_dir(Path): path to where sources are
            **kwargs(str | None): environment variables to be passed to build processes

        Returns:
            list[Path]: paths of produced packages
        """
        command = [self.build_command, "-r", str(self.paths.chroot)]
        command.extend(self.archbuild_flags)
        command.extend(["--"] + self.makechrootpkg_flags)
        command.extend(["--"] + self.makepkg_flags)
        self.logger.info("using %s for %s", command, self.package.base)

        environment: dict[str, str] = {
            key: value
            for key, value in kwargs.items()
            if value is not None
        }
        self.logger.info("using environment variables %s", environment)

        source_files = list(sources_dir.iterdir())
        check_output(
            *command,
            exception=BuildError.from_process(self.package.base),
            cwd=sources_dir,
            logger=self.logger,
            user=self.uid,
            environment=environment,
        )

        return self._package_archives(sources_dir, source_files)

    def init(self, sources_dir: Path, patches: list[PkgbuildPatch], local_version: str | None) -> str | None:
        """
        fetch package from git

        Args:
            sources_dir(Path): local path to fetch
            patches(list[PkgbuildPatch]): list of patches for the package
            local_version(str | None): local version of the package. If set and equal to current version, it will
                automatically bump pkgrel

        Returns:
            str | None: current commit sha if available
        """
        last_commit_sha = Sources.load(sources_dir, self.package, patches, self.paths)
        if local_version is None:
            return last_commit_sha  # there is no local package or pkgrel increment is disabled

        # load fresh package
        loaded_package = Package.from_build(sources_dir, self.architecture, None)
        if (pkgrel := loaded_package.next_pkgrel(local_version)) is not None:
            self.logger.info("package %s is the same as in repo, bumping pkgrel to %s", self.package.base, pkgrel)
            patch = PkgbuildPatch("pkgrel", pkgrel)
            patch.write(sources_dir / "PKGBUILD")

        return last_commit_sha

    def setup(self, sources_dir: Path) -> None:
        """
        setup chroot environment without building package itself. This function, in particular, useful in case if it is
        required to refresh pkgver to the actual value without package building

        Args:
            sources_dir(Path): path to where sources are
        """
        command = [self.build_command, "-r", str(self.paths.chroot)]
        command.extend(self.archbuild_flags)
        command.extend(["--"] + self.makechrootpkg_flags)
        command.extend(["--"] + self.makepkg_flags + ["--nobuild"])
        self.logger.info("using %s for %s", command, self.package.base)

        check_output(
            *command,
            exception=BuildError.from_process(self.package.base),
            cwd=sources_dir,
            logger=self.logger,
            user=self.uid,
        )
