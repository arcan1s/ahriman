#
# Copyright (c) 2021-2022 ahriman team.
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
from typing import List, Optional

from ahriman.core.util import check_output


class Sources:
    """
    helper to download package sources (PKGBUILD etc)
    :cvar logger: class logger
    """

    logger = logging.getLogger("build_details")

    _branch = "master"  # in case if BLM would like to change it
    _check_output = check_output

    @staticmethod
    def add(sources_dir: Path, *pattern: str) -> None:
        """
        track found files via git
        :param sources_dir: local path to git repository
        :param pattern: glob patterns
        """
        # glob directory to find files which match the specified patterns
        found_files: List[Path] = []
        for glob in pattern:
            found_files.extend(sources_dir.glob(glob))
        if not found_files:
            return  # no additional files found
        Sources.logger.info("found matching files %s", found_files)
        # add them to index
        Sources._check_output("git", "add", "--intent-to-add",
                              *[str(fn.relative_to(sources_dir)) for fn in found_files],
                              exception=None, cwd=sources_dir, logger=Sources.logger)

    @staticmethod
    def diff(sources_dir: Path) -> str:
        """
        generate diff from the current version and write it to the output file
        :param sources_dir: local path to git repository
        :return: patch as plain string
        """
        return Sources._check_output("git", "diff", exception=None, cwd=sources_dir, logger=Sources.logger)

    @staticmethod
    def fetch(sources_dir: Path, remote: Optional[str]) -> None:
        """
        either clone repository or update it to origin/`branch`
        :param sources_dir: local path to fetch
        :param remote: remote target (from where to fetch)
        """
        # local directory exists and there is .git directory
        is_initialized_git = (sources_dir / ".git").is_dir()
        if is_initialized_git and not Sources.has_remotes(sources_dir):
            # there is git repository, but no remote configured so far
            Sources.logger.info("skip update at %s because there are no branches configured", sources_dir)
            return

        if is_initialized_git:
            Sources.logger.info("update HEAD to remote at %s", sources_dir)
            Sources._check_output("git", "fetch", "origin", Sources._branch,
                                  exception=None, cwd=sources_dir, logger=Sources.logger)
        elif remote is None:
            Sources.logger.warning("%s is not initialized, but no remote provided", sources_dir)
        else:
            Sources.logger.info("clone remote %s to %s", remote, sources_dir)
            Sources._check_output("git", "clone", remote, str(sources_dir),
                                  exception=None, cwd=sources_dir, logger=Sources.logger)
        # and now force reset to our branch
        Sources._check_output("git", "checkout", "--force", Sources._branch,
                              exception=None, cwd=sources_dir, logger=Sources.logger)
        Sources._check_output("git", "reset", "--hard", f"origin/{Sources._branch}",
                              exception=None, cwd=sources_dir, logger=Sources.logger)

    @staticmethod
    def has_remotes(sources_dir: Path) -> bool:
        """
        check if there are remotes for the repository
        :param sources_dir: local path to git repository
        :return: True in case if there is any remote and false otherwise
        """
        remotes = Sources._check_output("git", "remote", exception=None, cwd=sources_dir, logger=Sources.logger)
        return bool(remotes)

    @staticmethod
    def init(sources_dir: Path) -> None:
        """
        create empty git repository at the specified path
        :param sources_dir: local path to sources
        """
        Sources._check_output("git", "init", "--initial-branch", Sources._branch,
                              exception=None, cwd=sources_dir, logger=Sources.logger)

    @staticmethod
    def load(sources_dir: Path, remote: str, patch: Optional[str]) -> None:
        """
        fetch sources from remote and apply patches
        :param sources_dir: local path to fetch
        :param remote: remote target (from where to fetch)
        :param patch: optional patch to be applied
        """
        Sources.fetch(sources_dir, remote)
        if patch is None:
            Sources.logger.info("no patches found")
            return
        Sources.patch_apply(sources_dir, patch)

    @staticmethod
    def patch_apply(sources_dir: Path, patch: str) -> None:
        """
        apply patches if any
        :param sources_dir: local path to directory with git sources
        :param patch: patch to be applied
        """
        # create patch
        Sources.logger.info("apply patch from database")
        Sources._check_output("git", "apply", "--ignore-space-change", "--ignore-whitespace",
                              exception=None, cwd=sources_dir, input_data=patch, logger=Sources.logger)

    @staticmethod
    def patch_create(sources_dir: Path, *pattern: str) -> str:
        """
        create patch set for the specified local path
        :param sources_dir: local path to git repository
        :param pattern: glob patterns
        :return: patch as plain text
        """
        Sources.add(sources_dir, *pattern)
        diff = Sources.diff(sources_dir)
        return f"{diff}\n"  # otherwise, patch will be broken
