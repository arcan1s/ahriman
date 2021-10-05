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
from typing import List

from ahriman.core.util import check_output


class Sources:
    """
    helper to download package sources (PKGBUILD etc)
    :cvar logger: class logger
    """

    logger = logging.getLogger("build_details")

    _check_output = check_output

    @staticmethod
    def add(local_path: Path, *pattern: str) -> None:
        """
        track found files via git
        :param local_path: local path to git repository
        :param pattern: glob patterns
        """
        # glob directory to find files which match the specified patterns
        found_files: List[Path] = []
        for glob in pattern:
            found_files.extend(local_path.glob(glob))
        Sources.logger.info("found matching files %s", found_files)
        # add them to index
        Sources._check_output("git", "add", "--intent-to-add", *[str(fn.relative_to(local_path)) for fn in found_files],
                              exception=None, cwd=local_path, logger=Sources.logger)

    @staticmethod
    def diff(local_path: Path, patch_path: Path) -> None:
        """
        generate diff from the current version and write it to the output file
        :param local_path: local path to git repository
        :param patch_path: path to result patch
        """
        patch = Sources._check_output("git", "diff", exception=None, cwd=local_path, logger=Sources.logger)
        patch_path.write_text(patch)

    @staticmethod
    def fetch(local_path: Path, remote: str, branch: str = "master") -> None:
        """
        either clone repository or update it to origin/`branch`
        :param local_path: local path to fetch
        :param remote: remote target (from where to fetch)
        :param branch: branch name to checkout, master by default
        """
        # local directory exists and there is .git directory
        if (local_path / ".git").is_dir():
            Sources.logger.info("update HEAD to remote to %s", local_path)
            Sources._check_output("git", "fetch", "origin", branch,
                                  exception=None, cwd=local_path, logger=Sources.logger)
        else:
            Sources.logger.info("clone remote %s to %s", remote, local_path)
            Sources._check_output("git", "clone", remote, str(local_path), exception=None, logger=Sources.logger)
        # and now force reset to our branch
        Sources._check_output("git", "checkout", "--force", branch,
                              exception=None, cwd=local_path, logger=Sources.logger)
        Sources._check_output("git", "reset", "--hard", f"origin/{branch}",
                              exception=None, cwd=local_path, logger=Sources.logger)

    @staticmethod
    def load(local_path: Path, remote: str, patch_dir: Path) -> None:
        """
        fetch sources from remote and apply patches
        :param local_path: local path to fetch
        :param remote: remote target (from where to fetch)
        :param patch_dir: path to directory with package patches
        """
        Sources.fetch(local_path, remote)
        Sources.patch_apply(local_path, patch_dir)

    @staticmethod
    def patch_apply(local_path: Path, patch_dir: Path) -> None:
        """
        apply patches if any
        :param local_path: local path to directory with git sources
        :param patch_dir: path to directory with package patches
        """
        # check if even there are patches
        if not patch_dir.is_dir():
            return  # no patches provided
        # find everything that looks like patch and sort it
        patches = sorted(patch_dir.glob("*.patch"))
        Sources.logger.info("found %s patches", patches)
        for patch in patches:
            Sources.logger.info("apply patch %s", patch.name)
            Sources._check_output("git", "apply", "--ignore-space-change", "--ignore-whitespace", str(patch),
                                  exception=None, cwd=local_path, logger=Sources.logger)

    @staticmethod
    def patch_create(local_path: Path, patch_path: Path, *pattern: str) -> None:
        """
        create patch set for the specified local path
        :param local_path: local path to git repository
        :param patch_path: path to result patch
        :param pattern: glob patterns
        """
        Sources.add(local_path, *pattern)
        Sources.diff(local_path, patch_path)
