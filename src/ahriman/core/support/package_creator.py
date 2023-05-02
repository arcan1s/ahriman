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
import shutil

from ahriman.core import context
from ahriman.core.build_tools.sources import Sources
from ahriman.core.configuration import Configuration
from ahriman.core.database import SQLite
from ahriman.core.log import LazyLogging
from ahriman.core.support.pkgbuild.pkgbuild_generator import PkgbuildGenerator
from ahriman.models.build_status import BuildStatus
from ahriman.models.context_key import ContextKey
from ahriman.models.package import Package


class PackageCreator(LazyLogging):
    """
    helper which creates packages based on pkgbuild generator

    Attributes:
        configuration(Configuration): configuration instance
        generator(PkgbuildGenerator): PKGBUILD generator instance
    """

    def __init__(self, configuration: Configuration, generator: PkgbuildGenerator) -> None:
        """
        default constructor

        Args:
            configuration(Configuration): configuration instance
            generator(PkgbuildGenerator): PKGBUILD generator instance
        """
        self.configuration = configuration
        self.generator = generator

    def run(self) -> None:
        """
        create new local package
        """
        local_path = self.configuration.repository_paths.cache_for(self.generator.pkgname)

        # clear old tree if any
        shutil.rmtree(local_path, ignore_errors=True)

        # create local tree
        local_path.mkdir(mode=0o755, parents=True, exist_ok=True)
        self.generator.write_pkgbuild(local_path)
        Sources.init(local_path)

        # register package
        ctx = context.get()
        database: SQLite = ctx.get(ContextKey("database", SQLite))
        _, architecture = self.configuration.check_loaded()
        package = Package.from_build(local_path, architecture)
        database.package_update(package, BuildStatus())
