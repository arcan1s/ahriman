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
from ahriman.core.archive.archive_tree import ArchiveTree
from ahriman.core.configuration import Configuration
from ahriman.core.sign.gpg import GPG
from ahriman.core.triggers import Trigger
from ahriman.models.package import Package
from ahriman.models.repository_id import RepositoryId
from ahriman.models.result import Result


class ArchiveTrigger(Trigger):
    """
    archive repository extension

    Attributes:
        paths(RepositoryPaths): repository paths instance
        tree(ArchiveTree): archive tree wrapper
    """

    def __init__(self, repository_id: RepositoryId, configuration: Configuration) -> None:
        """
        Args:
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
        """
        Trigger.__init__(self, repository_id, configuration)

        self.paths = configuration.repository_paths
        self.tree = ArchiveTree(self.paths, GPG(configuration).repository_sign_args)

    def on_result(self, result: Result, packages: list[Package]) -> None:
        """
        run trigger

        Args:
            result(Result): build result
            packages(list[Package]): list of all available packages
        """
        self.tree.symlinks_create(packages)

    def on_start(self) -> None:
        """
        trigger action which will be called at the start of the application
        """
        self.tree.tree_create()

    def on_stop(self) -> None:
        """
        trigger action which will be called before the stop of the application
        """
        repositories = set(self.tree.symlinks_fix())
        self.tree.directories_fix(repositories)
