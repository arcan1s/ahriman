#
# Copyright (c) 2021 ahriman team.
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
import logging

from pathlib import Path

from ahriman.core.util import check_output


class Sources:
    """
    helper to download package sources (PKGBUILD etc)
    """

    _check_output = check_output

    @staticmethod
    def fetch(local_path: Path, remote: str, branch: str = "master") -> None:
        """
        either clone repository or update it to origin/`branch`
        :param local_path: local path to fetch
        :param remote: remote target (from where to fetch)
        :param branch: branch name to checkout, master by default
        """
        logger = logging.getLogger("build_details")
        # local directory exists and there is .git directory
        if (local_path / ".git").is_dir():
            logger.info("update HEAD to remote to %s", local_path)
            Sources._check_output("git", "fetch", "origin", branch, exception=None, cwd=local_path, logger=logger)
        else:
            logger.info("clone remote %s to %s", remote, local_path)
            Sources._check_output("git", "clone", remote, str(local_path), exception=None, logger=logger)
        # and now force reset to our branch
        Sources._check_output("git", "checkout", "--force", branch, exception=None, cwd=local_path, logger=logger)
        Sources._check_output("git", "reset", "--hard", f"origin/{branch}",
                              exception=None, cwd=local_path, logger=logger)

    @staticmethod
    def load(local_path: Path, remote: str, patch_path: Path) -> None:
        """
        fetch sources from remote and apply patches
        :param local_path: local path to fetch
        :param remote: remote target (from where to fetch)
        :param patch_path: path to directory with package patches
        """
        Sources.fetch(local_path, remote)
        Sources.patch(local_path, patch_path)

    @staticmethod
    def patch(local_path: Path, patch_path: Path) -> None:
        """
        apply patches if any
        :param local_path: local path to directory with git sources
        :param patch_path: path to directory with package patches
        """
        # check if even there are patches
        if not patch_path.is_dir():
            return  # no patches provided
        logger = logging.getLogger("build_details")
        # find everything that looks like patch and sort it
        patches = sorted(patch_path.glob("*.patch"))
        logger.info("found %s patches", patches)
        for patch in patches:
            logger.info("apply patch %s", patch.name)
            Sources._check_output("git", "apply", "--ignore-space-change", "--ignore-whitespace", str(patch),
                                  exception=None, cwd=local_path, logger=logger)
