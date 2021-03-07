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
import os

from dataclasses import dataclass


@dataclass
class RepositoryPaths:
    root: str
    architecture: str

    @property
    def chroot(self) -> str:
        return os.path.join(self.root, 'chroot')

    @property
    def manual(self) -> str:
        return os.path.join(self.root, 'manual')

    @property
    def packages(self) -> str:
        return os.path.join(self.root, 'packages')

    @property
    def repository(self) -> str:
        return os.path.join(self.root, 'repository', self.architecture)

    @property
    def sources(self) -> str:
        return os.path.join(self.root, 'sources')

    def create_tree(self) -> None:
        os.makedirs(self.chroot, mode=0o755, exist_ok=True)
        os.makedirs(self.manual, mode=0o755, exist_ok=True)
        os.makedirs(self.packages, mode=0o755, exist_ok=True)
        os.makedirs(self.repository, mode=0o755, exist_ok=True)
        os.makedirs(self.sources, mode=0o755, exist_ok=True)