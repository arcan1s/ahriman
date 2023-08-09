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

from ahriman.core.log import LazyLogging
from ahriman.core.util import check_output, utcnow, walk
from ahriman.models.package import Package
from ahriman.models.pkgbuild_patch import PkgbuildPatch
from ahriman.models.remote_source import RemoteSource
from ahriman.models.repository_paths import RepositoryPaths


class Sources(LazyLogging):
    """
    helper to download package sources (PKGBUILD etc...)

    Attributes:
        DEFAULT_BRANCH(str): (class attribute) default branch to process git repositories.
            Must be used only for local stored repositories, use RemoteSource descriptor instead for real packages
        DEFAULT_COMMIT_AUTHOR(tuple[str, str]): (class attribute) default commit author to be used if none set
    """

    DEFAULT_BRANCH = "master"  # default fallback branch
    DEFAULT_COMMIT_AUTHOR = ("ahriman", "ahriman@localhost")

    _check_output = check_output

    @staticmethod
    def extend_architectures(sources_dir: Path, architecture: str) -> list[PkgbuildPatch]:
        """
        extend existing PKGBUILD with repository architecture

        Args:
            sources_dir(Path): local path to directory with source files
            architecture(str): repository architecture

        Returns:
            list[PkgbuildPatch]: generated patch for PKGBUILD architectures if required
        """
        architectures = Package.supported_architectures(sources_dir)
        if "any" in architectures:  # makepkg does not like when there is any other arch except for any
            return []
        architectures.add(architecture)
        return [PkgbuildPatch("arch", list(architectures))]

    @staticmethod
    def fetch(sources_dir: Path, remote: RemoteSource) -> None:
        """
        either clone repository or update it to origin/``remote.branch``

        Args:
            sources_dir(Path): local path to fetch
            remote(RemoteSource): remote target (from where to fetch)
        """
        instance = Sources()
        # local directory exists and there is .git directory
        is_initialized_git = (sources_dir / ".git").is_dir()
        if is_initialized_git and not instance.has_remotes(sources_dir):
            # there is git repository, but no remote configured so far
            instance.logger.info("skip update at %s because there are no branches configured", sources_dir)
            return

        branch = remote.branch or instance.DEFAULT_BRANCH
        if is_initialized_git:
            instance.logger.info("update HEAD to remote at %s using branch %s", sources_dir, branch)
            Sources._check_output("git", "fetch", "origin", branch, cwd=sources_dir, logger=instance.logger)
        elif remote.git_url is not None:
            instance.logger.info("clone remote %s to %s using branch %s", remote.git_url, sources_dir, branch)
            Sources._check_output("git", "clone", "--branch", branch, "--single-branch",
                                  remote.git_url, str(sources_dir), cwd=sources_dir.parent, logger=instance.logger)
        else:
            # it will cause an exception later
            instance.logger.error("%s is not initialized, but no remote provided", sources_dir)

        # and now force reset to our branch
        Sources._check_output("git", "checkout", "--force", branch, cwd=sources_dir, logger=instance.logger)
        Sources._check_output("git", "reset", "--hard", f"origin/{branch}", cwd=sources_dir, logger=instance.logger)

        # move content if required
        # we are using full path to source directory in order to make append possible
        pkgbuild_dir = remote.pkgbuild_dir or sources_dir.resolve()
        instance.move((sources_dir / pkgbuild_dir).resolve(), sources_dir)

    @staticmethod
    def has_remotes(sources_dir: Path) -> bool:
        """
        check if there are remotes for the repository

        Args:
            sources_dir(Path): local path to git repository

        Returns:
            bool: True in case if there is any remote and false otherwise
        """
        instance = Sources()
        remotes = Sources._check_output("git", "remote", cwd=sources_dir, logger=instance.logger)
        return bool(remotes)

    @staticmethod
    def init(sources_dir: Path) -> None:
        """
        create empty git repository at the specified path

        Args:
            sources_dir(Path): local path to sources
        """
        instance = Sources()
        if not (sources_dir / ".git").is_dir():
            # skip initializing in case if it was already
            Sources._check_output("git", "init", "--initial-branch", instance.DEFAULT_BRANCH,
                                  cwd=sources_dir, logger=instance.logger)

        # extract local files...
        files = ["PKGBUILD", ".SRCINFO"] + [str(path) for path in Package.local_files(sources_dir)]
        instance.add(sources_dir, *files)
        # ...and commit them
        instance.commit(sources_dir)

    @staticmethod
    def load(sources_dir: Path, package: Package, patches: list[PkgbuildPatch], paths: RepositoryPaths) -> None:
        """
        fetch sources from remote and apply patches

        Args:
            sources_dir(Path): local path to fetch
            package(Package): package definitions
            patches(list[PkgbuildPatch]): optional patch to be applied
            paths(RepositoryPaths): repository paths instance
        """
        instance = Sources()
        if (cache_dir := paths.cache_for(package.base)).is_dir() and cache_dir != sources_dir:
            # no need to clone whole repository, just copy from cache first
            shutil.copytree(cache_dir, sources_dir, dirs_exist_ok=True)
        instance.fetch(sources_dir, package.remote)

        patches.extend(instance.extend_architectures(sources_dir, paths.architecture))
        for patch in patches:
            instance.patch_apply(sources_dir, patch)

    @staticmethod
    def patch_create(sources_dir: Path, *pattern: str) -> str:
        """
        create patch set for the specified local path

        Args:
            sources_dir(Path): local path to git repository
            *pattern(str): glob patterns

        Returns:
            str: patch as plain text
        """
        instance = Sources()
        instance.add(sources_dir, *pattern, intent_to_add=True)
        diff = instance.diff(sources_dir)
        return f"{diff}\n"  # otherwise, patch will be broken

    @staticmethod
    def push(sources_dir: Path, remote: RemoteSource, *pattern: str,
             commit_author: tuple[str, str] | None = None) -> None:
        """
        commit selected changes and push files to the remote repository

        Args:
            sources_dir(Path): local path to git repository
            remote(RemoteSource): remote target, branch and url
            *pattern(str): glob patterns
            commit_author(tuple[str, str] | None, optional): commit author if any (Default value = None)
        """
        instance = Sources()
        instance.add(sources_dir, *pattern)
        if not instance.commit(sources_dir, commit_author=commit_author):
            return  # no changes to push, just skip action

        git_url, branch = remote.git_source()
        Sources._check_output("git", "push", git_url, branch, cwd=sources_dir, logger=instance.logger)

    def add(self, sources_dir: Path, *pattern: str, intent_to_add: bool = False) -> None:
        """
        track found files via git

        Args:
            sources_dir(Path): local path to git repository
            *pattern(str): glob patterns
            intent_to_add(bool, optional): record only the fact that it will be added later, acts as
                --intent-to-add git flag (Default value = False)
        """
        # glob directory to find files which match the specified patterns
        found_files: list[Path] = []
        for glob in pattern:
            found_files.extend(sources_dir.glob(glob))
        if not found_files:
            return  # no additional files found
        self.logger.info("found matching files %s", found_files)
        # add them to index
        args = ["--intent-to-add"] if intent_to_add else []
        Sources._check_output("git", "add", *args, *[str(fn.relative_to(sources_dir)) for fn in found_files],
                              cwd=sources_dir, logger=self.logger)

    def commit(self, sources_dir: Path, message: str | None = None,
               commit_author: tuple[str, str] | None = None) -> bool:
        """
        commit changes

        Args:
            sources_dir(Path): local path to git repository
            message(str | None, optional): optional commit message if any. If none set, message will be generated
                according to the current timestamp (Default value = None)
            commit_author(tuple[str, str] | None, optional): optional commit author if any (Default value = None)

        Returns:
            bool: True in case if changes have been committed and False otherwise
        """
        if not self.has_changes(sources_dir):
            return False  # nothing to commit

        if message is None:
            message = f"Autogenerated commit at {utcnow()}"
        args = ["--message", message]
        environment: dict[str, str] = {}

        if commit_author is None:
            commit_author = self.DEFAULT_COMMIT_AUTHOR
        user, email = commit_author
        environment["GIT_AUTHOR_NAME"] = environment["GIT_COMMITTER_NAME"] = user
        environment["GIT_AUTHOR_EMAIL"] = environment["GIT_COMMITTER_EMAIL"] = email

        Sources._check_output("git", "commit", *args, cwd=sources_dir, logger=self.logger, environment=environment)

        return True

    def diff(self, sources_dir: Path) -> str:
        """
        generate diff from the current version and write it to the output file

        Args:
            sources_dir(Path): local path to git repository

        Returns:
            str: patch as plain string
        """
        return Sources._check_output("git", "diff", cwd=sources_dir, logger=self.logger)

    def has_changes(self, sources_dir: Path) -> bool:
        """
        check if there are changes in current git tree

        Args:
            sources_dir(Path): local path to git repository

        Returns:
            bool: True if there are uncommitted changes and False otherwise
        """
        # there is --exit-code argument to diff, however, there might be other process errors
        changes = Sources._check_output("git", "diff", "--cached", "--name-only", cwd=sources_dir, logger=self.logger)
        return bool(changes)

    def move(self, pkgbuild_dir: Path, sources_dir: Path) -> None:
        """
        move content from pkgbuild_dir to sources_dir

        Args:
            pkgbuild_dir(Path): path to directory with pkgbuild from which need to move
            sources_dir(Path): path to target directory
        """
        del self
        if pkgbuild_dir == sources_dir:
            return  # directories are the same, no need to move
        for src in walk(pkgbuild_dir):
            dst = sources_dir / src.relative_to(pkgbuild_dir)
            shutil.move(src, dst)

    def patch_apply(self, sources_dir: Path, patch: PkgbuildPatch) -> None:
        """
        apply patches if any

        Args:
            sources_dir(Path): local path to directory with git sources
            patch(PkgbuildPatch): patch to be applied
        """
        # create patch
        self.logger.info("apply patch %s from database at %s", patch.key, sources_dir)
        if patch.is_plain_diff:
            Sources._check_output("git", "apply", "--ignore-space-change", "--ignore-whitespace",
                                  cwd=sources_dir, input_data=patch.serialize(), logger=self.logger)
        else:
            patch.write(sources_dir / "PKGBUILD")
