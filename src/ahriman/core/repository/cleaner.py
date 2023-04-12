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

from pathlib import Path

from ahriman.core.repository.repository_properties import RepositoryProperties


class Cleaner(RepositoryProperties):
    """
    trait to clean common repository objects
    """

    def clear_cache(self) -> None:
        """
        clear cache directory
        """
        self.logger.info("clear packages sources cache directory")
        for package in self.paths.cache.iterdir():
            shutil.rmtree(package)

    def clear_chroot(self) -> None:
        """
        clear cache directory. Warning: this method is architecture independent and will clear every chroot
        """
        self.logger.info("clear build chroot directory")
        for chroot in self.paths.chroot.iterdir():
            shutil.rmtree(chroot)

    def clear_packages(self) -> None:
        """
        clear directory with built packages (NOT repository itself)
        """
        self.logger.info("clear built packages directory")
        for package in self.packages_built():
            package.unlink()

    def clear_pacman(self) -> None:
        """
        clear directory with pacman databases
        """
        self.logger.info("clear pacman database directory")
        for pacman in self.paths.pacman.iterdir():
            shutil.rmtree(pacman)

    def clear_queue(self) -> None:
        """
        clear packages which were queued for the update
        """
        self.logger.info("clear build queue")
        self.database.build_queue_clear(None)

    def packages_built(self) -> list[Path]:
        """
        get list of files in built packages directory

        Returns:
            list[Path]: list of filenames from the directory

        Raises:
            NotImplementedError: not implemented method
        """
        raise NotImplementedError
