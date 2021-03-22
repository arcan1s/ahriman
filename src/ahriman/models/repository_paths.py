#
# Copyright (c) 2021 Evgenii Alekseev.
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
from pathlib import Path

from dataclasses import dataclass


@dataclass
class RepositoryPaths:
    """
    repository paths holder. For the most operations with paths you want to use this object
    :ivar root: repository root (i.e. ahriman home)
    :ivar architecture: repository architecture
    """

    root: Path
    architecture: str

    @property
    def cache(self) -> Path:
        """
        :return: directory for packages cache (mainly used for VCS packages)
        """
        return self.root / "cache"

    @property
    def chroot(self) -> Path:
        """
        :return: directory for devtools chroot
        """
        # for the chroot directory devtools will create own tree and we don"t have to specify architecture here
        return self.root / "chroot"

    @property
    def manual(self) -> Path:
        """
        :return: directory for manual updates (i.e. from add command)
        """
        return self.root / "manual" / self.architecture

    @property
    def packages(self) -> Path:
        """
        :return: directory for built packages
        """
        return self.root / "packages" / self.architecture

    @property
    def repository(self) -> Path:
        """
        :return: repository directory
        """
        return self.root / "repository" / self.architecture

    @property
    def sources(self) -> Path:
        """
        :return: directory for downloaded PKGBUILDs for current build
        """
        return self.root / "sources" / self.architecture

    def create_tree(self) -> None:
        """
        create ahriman working tree
        """
        self.cache.mkdir(mode=0o755, parents=True, exist_ok=True)
        self.chroot.mkdir(mode=0o755, parents=True, exist_ok=True)
        self.manual.mkdir(mode=0o755, parents=True, exist_ok=True)
        self.packages.mkdir(mode=0o755, parents=True, exist_ok=True)
        self.repository.mkdir(mode=0o755, parents=True, exist_ok=True)
        self.sources.mkdir(mode=0o755, parents=True, exist_ok=True)
