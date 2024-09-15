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
import shutil

from pathlib import Path

from ahriman.core import context
from ahriman.core.build_tools.sources import Sources
from ahriman.core.configuration import Configuration
from ahriman.core.status import Client
from ahriman.core.support.pkgbuild.pkgbuild_generator import PkgbuildGenerator
from ahriman.models.package import Package


class PackageCreator:
    """
    helper which creates packages based on pkgbuild generator

    Attributes:
        configuration(Configuration): configuration instance
        generator(PkgbuildGenerator): PKGBUILD generator instance
    """

    def __init__(self, configuration: Configuration, generator: PkgbuildGenerator) -> None:
        """
        Args:
            configuration(Configuration): configuration instance
            generator(PkgbuildGenerator): PKGBUILD generator instance
        """
        self.configuration = configuration
        self.generator = generator

    def package_create(self, path: Path) -> None:
        """
        create package files

        Args:
            path(Path): path to directory with package files
        """
        # clear old tree if any
        shutil.rmtree(path, ignore_errors=True)

        # create local tree
        path.mkdir(mode=0o755, parents=True, exist_ok=True)
        self.generator.write_pkgbuild(path)
        Sources.init(path)

    def package_register(self, path: Path) -> None:
        """
        register package in build worker

        Args:
            path(Path): path to directory with package files
        """
        ctx = context.get()
        reporter = ctx.get(Client)
        _, repository_id = self.configuration.check_loaded()
        package = Package.from_build(path, repository_id.architecture, None)

        reporter.set_unknown(package)

    def run(self) -> None:
        """
        create new local package
        """
        local_path = self.configuration.repository_paths.cache_for(self.generator.pkgname)
        self.package_create(local_path)
        self.package_register(local_path)
