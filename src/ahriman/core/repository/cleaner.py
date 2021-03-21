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
import shutil

from typing import List

from ahriman.core.repository.properties import Properties


class Cleaner(Properties):
    """
    trait to clean common repository objects
    """

    def packages_built(self) -> List[str]:
        """
        get list of files in built packages directory
        :return: list of filenames from the directory
        """
        raise NotImplementedError

    def clear_build(self) -> None:
        """
        clear sources directory
        """
        self.logger.info("clear package sources directory")
        for package in os.listdir(self.paths.sources):
            shutil.rmtree(os.path.join(self.paths.sources, package))

    def clear_cache(self) -> None:
        """
        clear cache directory
        """
        self.logger.info("clear packages sources cache directory")
        for package in os.listdir(self.paths.cache):
            shutil.rmtree(os.path.join(self.paths.cache, package))

    def clear_chroot(self) -> None:
        """
        clear cache directory. Warning: this method is architecture independent and will clear every chroot
        """
        self.logger.info("clear build chroot directory")
        for chroot in os.listdir(self.paths.chroot):
            shutil.rmtree(os.path.join(self.paths.chroot, chroot))

    def clear_manual(self) -> None:
        """
        clear directory with manual package updates
        """
        self.logger.info("clear manual packages")
        for package in os.listdir(self.paths.manual):
            shutil.rmtree(os.path.join(self.paths.manual, package))

    def clear_packages(self) -> None:
        """
        clear directory with built packages (NOT repository itself)
        """
        self.logger.info("clear built packages directory")
        for package in self.packages_built():
            os.remove(package)
