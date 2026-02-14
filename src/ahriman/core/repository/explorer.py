#
# Copyright (c) 2021-2026 ahriman team.
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

from ahriman.core.configuration import Configuration
from ahriman.models.repository_id import RepositoryId
from ahriman.models.repository_paths import RepositoryPaths


class Explorer:
    """
    helper to read filesystem and find created repositories
    """

    @staticmethod
    def repositories_extract(configuration: Configuration, repository: str | None = None,
                             architecture: str | None = None) -> list[RepositoryId]:
        """
        get known architectures

        Args:
            configuration(Configuration): configuration instance
            repository(str | None, optional): predefined repository name if available (Default value = None)
            architecture(str | None, optional): predefined repository architecture if available (Default value = None)

        Returns:
            list[RepositoryId]: list of repository names and architectures for which tree is created
        """
        # pylint, wtf???
        root = configuration.getpath("repository", "root")  # pylint: disable=assignment-from-no-return

        # extract repository names first
        if repository is not None:
            repositories: Iterable[str] = [repository]
        elif from_filesystem := RepositoryPaths.known_repositories(root):
            repositories = from_filesystem
        else:  # try to read configuration now
            repositories = [configuration.get("repository", "name")]

        # extract architecture names
        if architecture is not None:
            parsed = set(
                RepositoryId(architecture, repository)
                for repository in repositories
            )
        else:  # try to read from file system
            parsed = set(
                RepositoryId(architecture, repository)
                for repository in repositories
                for architecture in RepositoryPaths.known_architectures(root, repository)
            )

        return sorted(parsed)
