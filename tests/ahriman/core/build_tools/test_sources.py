import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.core.build_tools.sources import Sources
from ahriman.core.exceptions import CalledProcessError
from ahriman.models.package import Package
from ahriman.models.package_source import PackageSource
from ahriman.models.pkgbuild_patch import PkgbuildPatch
from ahriman.models.remote_source import RemoteSource
from ahriman.models.repository_paths import RepositoryPaths


def test_changes(mocker: MockerFixture) -> None:
    """
    must calculate changes from the last known commit
    """
    fetch_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.fetch_until")
    diff_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.diff", return_value="diff")
    local = Path("local")
    last_commit_sha = "sha"

    assert Sources.changes(local, last_commit_sha) == "diff"
    fetch_mock.assert_called_once_with(local, commit_sha=last_commit_sha)
    diff_mock.assert_called_once_with(local, last_commit_sha)


def test_changes_skip(mocker: MockerFixture) -> None:
    """
    must return none in case if commit sha is not available
    """
    fetch_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.fetch_until")
    diff_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.diff")

    assert Sources.changes(Path("local"), None) is None
    fetch_mock.assert_not_called()
    diff_mock.assert_not_called()


def test_changes_unknown_commit(mocker: MockerFixture) -> None:
    """
    must return none in case if commit sha wasn't found at the required depth
    """
    mocker.patch("ahriman.core.build_tools.sources.Sources.fetch_until", return_value=None)
    diff_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.diff")

    assert Sources.changes(Path("local"), "sha") is None
    diff_mock.assert_not_called()


def test_extend_architectures(mocker: MockerFixture) -> None:
    """
    must update available architecture list
    """
    mocker.patch("pathlib.Path.is_file", return_value=True)
    architectures_mock = mocker.patch("ahriman.models.package.Package.supported_architectures", return_value={"x86_64"})

    assert Sources.extend_architectures(Path("local"), "i686") == [PkgbuildPatch("arch", list({"x86_64", "i686"}))]
    architectures_mock.assert_called_once_with(Path("local"))


def test_extend_architectures_any(mocker: MockerFixture) -> None:
    """
    must skip architecture patching in case if there is any architecture
    """
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("ahriman.models.package.Package.supported_architectures", return_value={"any"})
    assert Sources.extend_architectures(Path("local"), "i686") == []


def test_fetch_empty(remote_source: RemoteSource, mocker: MockerFixture) -> None:
    """
    must do nothing in case if no branches available
    """
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("ahriman.core.build_tools.sources.Sources.has_remotes", return_value=False)
    head_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.head", return_value="sha")
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.check_output")

    local = Path("local")
    assert Sources.fetch(local, remote_source) == "sha"
    head_mock.assert_called_once_with(local)
    check_output_mock.assert_not_called()


def test_fetch_existing(sources: Sources, remote_source: RemoteSource, mocker: MockerFixture) -> None:
    """
    must fetch new package via fetch command
    """
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("ahriman.core.build_tools.sources.Sources.has_remotes", return_value=True)
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.check_output")
    fetch_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.fetch_until")
    move_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.move")
    head_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.head", return_value="sha")

    local = Path("local")
    assert sources.fetch(local, remote_source) == "sha"
    fetch_mock.assert_called_once_with(local, branch=remote_source.branch)
    check_output_mock.assert_has_calls([
        MockCall(*sources.git(), "checkout", "--force", remote_source.branch,
                 cwd=local, logger=pytest.helpers.anyvar(int)),
        MockCall(*sources.git(), "reset", "--quiet", "--hard", f"origin/{remote_source.branch}",
                 cwd=local, logger=pytest.helpers.anyvar(int)),
    ])
    move_mock.assert_called_once_with(local.resolve(), local)
    head_mock.assert_called_once_with(local)


def test_fetch_new(sources: Sources, remote_source: RemoteSource, mocker: MockerFixture) -> None:
    """
    must fetch new package via clone command
    """
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.check_output")
    move_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.move")
    head_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.head", return_value="sha")

    local = Path("local")
    assert sources.fetch(local, remote_source) == "sha"
    check_output_mock.assert_has_calls([
        MockCall(*sources.git(), "clone", "--quiet", "--depth", "1", "--branch", remote_source.branch,
                 "--single-branch", remote_source.git_url, str(local),
                 cwd=local.parent, logger=pytest.helpers.anyvar(int)),
        MockCall(*sources.git(), "checkout", "--force", remote_source.branch,
                 cwd=local, logger=pytest.helpers.anyvar(int)),
        MockCall(*sources.git(), "reset", "--quiet", "--hard", f"origin/{remote_source.branch}",
                 cwd=local, logger=pytest.helpers.anyvar(int))
    ])
    move_mock.assert_called_once_with(local.resolve(), local)
    head_mock.assert_called_once_with(local)


def test_fetch_new_without_remote(sources: Sources, mocker: MockerFixture) -> None:
    """
    must fetch nothing in case if no remote set
    """
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.check_output")
    move_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.move")
    head_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.head", return_value="sha")

    local = Path("local")
    assert sources.fetch(local, RemoteSource(source=PackageSource.Archive)) == "sha"
    check_output_mock.assert_has_calls([
        MockCall(*sources.git(), "checkout", "--force", sources.DEFAULT_BRANCH,
                 cwd=local, logger=pytest.helpers.anyvar(int)),
        MockCall(*sources.git(), "reset", "--quiet", "--hard", f"origin/{sources.DEFAULT_BRANCH}",
                 cwd=local, logger=pytest.helpers.anyvar(int))
    ])
    move_mock.assert_called_once_with(local.resolve(), local)
    head_mock.assert_called_once_with(local)


def test_fetch_relative(remote_source: RemoteSource, mocker: MockerFixture) -> None:
    """
    must process move correctly on relative directory
    """
    mocker.patch("ahriman.core.build_tools.sources.check_output")
    move_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.move")
    head_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.head", return_value="sha")

    local = Path("local")
    assert Sources.fetch(local, remote_source) == "sha"
    move_mock.assert_called_once_with(local.resolve(), local)
    head_mock.assert_called_once_with(local)


def test_has_remotes(sources: Sources, mocker: MockerFixture) -> None:
    """
    must ask for remotes
    """
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.check_output", return_value="origin")

    local = Path("local")
    assert sources.has_remotes(local)
    check_output_mock.assert_called_once_with(*sources.git(), "remote", cwd=local, logger=pytest.helpers.anyvar(int))


def test_has_remotes_empty(mocker: MockerFixture) -> None:
    """
    must ask for remotes and return false in case if no remotes found
    """
    mocker.patch("ahriman.core.build_tools.sources.check_output", return_value="")
    assert not Sources.has_remotes(Path("local"))


def test_init(sources: Sources, mocker: MockerFixture) -> None:
    """
    must create empty repository at the specified path
    """
    mocker.patch("ahriman.models.package.Package.local_files", return_value=[Path("local")])
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    add_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.add")
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.check_output")
    commit_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.commit")

    local = Path("local")
    sources.init(local)
    check_output_mock.assert_called_once_with(*sources.git(), "init", "--quiet", "--initial-branch",
                                              sources.DEFAULT_BRANCH, cwd=local, logger=pytest.helpers.anyvar(int))
    add_mock.assert_called_once_with(local, "PKGBUILD", ".SRCINFO", "local")
    commit_mock.assert_called_once_with(local)


def test_init_skip(mocker: MockerFixture) -> None:
    """
    must skip git init if it was already
    """
    mocker.patch("ahriman.models.package.Package.local_files", return_value=[Path("local")])
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("ahriman.core.build_tools.sources.Sources.add")
    mocker.patch("ahriman.core.build_tools.sources.Sources.commit")
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.check_output")

    Sources.init(Path("local"))
    check_output_mock.assert_not_called()


def test_load(package_ahriman: Package, repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must load packages sources correctly
    """
    patch = PkgbuildPatch(None, "patch")
    path = Path("local")
    fetch_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.fetch", return_value="sha")
    patch_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.patch_apply")
    architectures_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.extend_architectures", return_value=[])

    assert Sources.load(path, package_ahriman, [patch], repository_paths) == "sha"
    fetch_mock.assert_called_once_with(path, package_ahriman.remote)
    patch_mock.assert_called_once_with(path, patch)
    architectures_mock.assert_called_once_with(path, repository_paths.repository_id.architecture)


def test_load_no_patch(package_ahriman: Package, repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must load packages sources correctly without patches
    """
    mocker.patch("pathlib.Path.is_dir", return_value=False)
    mocker.patch("ahriman.core.build_tools.sources.Sources.fetch", return_value="sha")
    mocker.patch("ahriman.core.build_tools.sources.Sources.extend_architectures", return_value=[])
    patch_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.patch_apply")

    assert Sources.load(Path("local"), package_ahriman, [], repository_paths) == "sha"
    patch_mock.assert_not_called()


def test_load_with_cache(package_ahriman: Package, repository_paths: RepositoryPaths, mocker: MockerFixture) -> None:
    """
    must load sources by using local cache
    """
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    copytree_mock = mocker.patch("shutil.copytree")
    mocker.patch("ahriman.core.build_tools.sources.Sources.fetch", return_value="sha")
    mocker.patch("ahriman.core.build_tools.sources.Sources.extend_architectures", return_value=[])

    assert Sources.load(Path("local"), package_ahriman, [], repository_paths) == "sha"
    copytree_mock.assert_called_once()  # we do not check full command here, sorry


def test_patch_create(mocker: MockerFixture) -> None:
    """
    must create patch set for the package
    """
    add_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.add")
    diff_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.diff")

    Sources.patch_create(Path("local"), "glob")
    add_mock.assert_called_once_with(Path("local"), "glob", intent_to_add=True)
    diff_mock.assert_called_once_with(Path("local"))


def test_patch_create_with_newline(mocker: MockerFixture) -> None:
    """
    created patch must have new line at the end
    """
    mocker.patch("ahriman.core.build_tools.sources.Sources.add")
    mocker.patch("ahriman.core.build_tools.sources.Sources.diff", return_value="diff")
    assert Sources.patch_create(Path("local"), "glob").endswith("\n")


def test_push(package_ahriman: Package, sources: Sources, mocker: MockerFixture) -> None:
    """
    must correctly push files to remote repository
    """
    add_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.add")
    commit_mock = mocker.patch("ahriman.core.build_tools.sources.Sources.commit", return_value=True)
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.check_output")

    commit_author = ("commit author", "user@host")
    local = Path("local")
    sources.push(local, package_ahriman.remote, "glob", commit_author=commit_author)
    add_mock.assert_called_once_with(local, "glob")
    commit_mock.assert_called_once_with(local, commit_author=commit_author)
    check_output_mock.assert_called_once_with(
        *sources.git(), "push", "--quiet", package_ahriman.remote.git_url, package_ahriman.remote.branch,
        cwd=local, logger=pytest.helpers.anyvar(int))


def test_push_skipped(package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must skip push if no changes were committed
    """
    mocker.patch("ahriman.core.build_tools.sources.Sources.add")
    mocker.patch("ahriman.core.build_tools.sources.Sources.commit", return_value=False)
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.check_output")

    Sources.push(Path("local"), package_ahriman.remote)
    check_output_mock.assert_not_called()


def test_add(sources: Sources, mocker: MockerFixture) -> None:
    """
    must add files to git
    """
    glob_mock = mocker.patch("pathlib.Path.glob", return_value=[Path("local/1"), Path("local/2")])
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.check_output")

    local = Path("local")
    sources.add(local, "pattern1", "pattern2")
    glob_mock.assert_has_calls([MockCall("pattern1"), MockCall("pattern2")])
    check_output_mock.assert_called_once_with(
        *sources.git(), "add", "1", "2", "1", "2", cwd=local, logger=sources.logger
    )


def test_add_intent_to_add(sources: Sources, mocker: MockerFixture) -> None:
    """
    must add files to git with --intent-to-add flag
    """
    glob_mock = mocker.patch("pathlib.Path.glob", return_value=[Path("local/1"), Path("local/2")])
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.check_output")

    local = Path("local")
    sources.add(local, "pattern1", "pattern2", intent_to_add=True)
    glob_mock.assert_has_calls([MockCall("pattern1"), MockCall("pattern2")])
    check_output_mock.assert_called_once_with(
        *sources.git(), "add", "--intent-to-add", "1", "2", "1", "2", cwd=local, logger=sources.logger
    )


def test_add_skip(sources: Sources, mocker: MockerFixture) -> None:
    """
    must skip addition of files to index if no fields found
    """
    mocker.patch("pathlib.Path.glob", return_value=[])
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.check_output")

    sources.add(Path("local"), "pattern1")
    check_output_mock.assert_not_called()


def test_commit(sources: Sources, mocker: MockerFixture) -> None:
    """
    must commit changes
    """
    mocker.patch("ahriman.core.build_tools.sources.Sources.has_changes", return_value=True)
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.check_output")

    local = Path("local")
    message = "Commit message"
    user, email = sources.DEFAULT_COMMIT_AUTHOR
    assert sources.commit(local, message=message)
    check_output_mock.assert_called_once_with(
        *sources.git(), "-c", f"user.email=\"{email}\"", "-c", f"user.name=\"{user}\"",
        "commit", "--quiet", "--message", message, cwd=local, logger=sources.logger
    )


def test_commit_no_changes(sources: Sources, mocker: MockerFixture) -> None:
    """
    must skip commit if there are no changes
    """
    mocker.patch("ahriman.core.build_tools.sources.Sources.has_changes", return_value=False)
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.check_output")

    assert not sources.commit(Path("local"))
    check_output_mock.assert_not_called()


def test_commit_author(sources: Sources, mocker: MockerFixture) -> None:
    """
    must commit changes with commit author
    """
    mocker.patch("ahriman.core.build_tools.sources.Sources.has_changes", return_value=True)
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.check_output")

    local = Path("local")
    message = "Commit message"
    user, email = author = ("commit author", "user@host")
    assert sources.commit(Path("local"), message=message, commit_author=author)
    check_output_mock.assert_called_once_with(
        *sources.git(), "-c", f"user.email=\"{email}\"", "-c", f"user.name=\"{user}\"",
        "commit", "--quiet", "--message", message, cwd=local, logger=sources.logger
    )


def test_commit_autogenerated_message(sources: Sources, mocker: MockerFixture) -> None:
    """
    must commit changes with autogenerated commit message
    """
    mocker.patch("ahriman.core.build_tools.sources.Sources.has_changes", return_value=True)
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.check_output")

    local = Path("local")
    assert sources.commit(Path("local"))
    user, email = sources.DEFAULT_COMMIT_AUTHOR
    check_output_mock.assert_called_once_with(
        *sources.git(), "-c", f"user.email=\"{email}\"", "-c", f"user.name=\"{user}\"",
        "commit", "--quiet", "--message", pytest.helpers.anyvar(str, strict=True), cwd=local, logger=sources.logger
    )


def test_diff(sources: Sources, mocker: MockerFixture) -> None:
    """
    must calculate diff
    """
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.check_output")

    local = Path("local")
    assert sources.diff(local)
    check_output_mock.assert_called_once_with(*sources.git(), "diff", cwd=local, logger=sources.logger)


def test_diff_specific(sources: Sources, mocker: MockerFixture) -> None:
    """
    must calculate diff from specific ref
    """
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.check_output")

    local = Path("local")
    assert sources.diff(local, "hash")
    check_output_mock.assert_called_once_with(*sources.git(), "diff", "hash", cwd=local, logger=sources.logger)


def test_fetch_until(sources: Sources, mocker: MockerFixture) -> None:
    """
    must fetch until the specified commit
    """
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.check_output", side_effect=[
        "",
        CalledProcessError(1, ["command"], "error"),
        "",
        "",
    ])
    local = Path("local")
    last_commit_sha = "sha"

    assert sources.fetch_until(local, branch="master", commit_sha="sha") == last_commit_sha
    check_output_mock.assert_has_calls([
        MockCall(*sources.git(), "fetch", "--quiet", "--depth", "1", "origin", "master",
                 cwd=local, logger=sources.logger),
        MockCall(*sources.git(), "cat-file", "-e", last_commit_sha, cwd=local, logger=sources.logger),
        MockCall(*sources.git(), "fetch", "--quiet", "--depth", "2", "origin", "master",
                 cwd=local, logger=sources.logger),
        MockCall(*sources.git(), "cat-file", "-e", last_commit_sha, cwd=local, logger=sources.logger),
    ])


def test_fetch_until_first(sources: Sources, mocker: MockerFixture) -> None:
    """
    must fetch first commit only
    """
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.check_output")
    local = Path("local")

    assert sources.fetch_until(local, branch="master") == "HEAD"
    check_output_mock.assert_has_calls([
        MockCall(*sources.git(), "fetch", "--quiet", "--depth", "1", "origin", "master",
                 cwd=local, logger=sources.logger),
        MockCall(*sources.git(), "cat-file", "-e", "HEAD", cwd=local, logger=sources.logger),
    ])


def test_fetch_until_all_branches(sources: Sources, mocker: MockerFixture) -> None:
    """
    must fetch all branches
    """
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.check_output")
    local = Path("local")

    assert sources.fetch_until(local) == "HEAD"
    check_output_mock.assert_has_calls([
        MockCall(*sources.git(), "fetch", "--quiet", "--depth", "1", cwd=local, logger=sources.logger),
        MockCall(*sources.git(), "cat-file", "-e", "HEAD", cwd=local, logger=sources.logger),
    ])


def test_fetch_until_not_found(sources: Sources, mocker: MockerFixture) -> None:
    """
    must return None in case if no commit found at the required maximal depth
    """
    mocker.patch("ahriman.core.build_tools.sources.check_output", side_effect=[
        "",
        CalledProcessError(1, ["command"], "error"),
        "",
        CalledProcessError(1, ["command"], "error"),
    ])
    assert sources.fetch_until(Path("local"), branch="master", commit_sha="sha", max_depth=2) is None


def test_git(sources: Sources) -> None:
    """
    must correctly generate git command
    """
    assert sources.git() == ["git", "-c", "init.defaultBranch=\"master\""]


def test_git_overrides(sources: Sources) -> None:
    """
    must correctly generate git command with additional settings
    """
    assert sources.git({"user.email": "ahriman@localhost"}) == [
        "git", "-c", "init.defaultBranch=\"master\"", "-c", "user.email=\"ahriman@localhost\""
    ]


def test_has_changes(sources: Sources, mocker: MockerFixture) -> None:
    """
    must correctly identify if there are changes
    """
    local = Path("local")

    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.check_output", return_value="M a.txt")
    assert sources.has_changes(local)
    check_output_mock.assert_called_once_with(*sources.git(), "diff", "--cached", "--name-only",
                                              cwd=local, logger=sources.logger)

    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.check_output", return_value="")
    assert not sources.has_changes(local)
    check_output_mock.assert_called_once_with(*sources.git(), "diff", "--cached", "--name-only",
                                              cwd=local, logger=sources.logger)


def test_head(sources: Sources, mocker: MockerFixture) -> None:
    """
    must correctly define HEAD hash
    """
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.check_output", return_value="sha")
    local = Path("local")

    assert sources.head(local) == "sha"
    check_output_mock.assert_called_once_with(*sources.git(), "rev-parse", "HEAD", cwd=local, logger=sources.logger)


def test_head_specific(sources: Sources, mocker: MockerFixture) -> None:
    """
    must correctly define ref hash
    """
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.check_output", return_value="sha")
    local = Path("local")

    assert sources.head(local, "master") == "sha"
    check_output_mock.assert_called_once_with(*sources.git(), "rev-parse", "master", cwd=local, logger=sources.logger)


def test_move(sources: Sources, mocker: MockerFixture) -> None:
    """
    must move content between directories
    """
    mocker.patch("ahriman.core.build_tools.sources.walk", return_value=[Path("/source/path")])
    move_mock = mocker.patch("shutil.move")

    sources.move(Path("/source"), Path("/destination"))
    move_mock.assert_called_once_with(Path("/source/path"), Path("/destination/path"))


def test_move_same(sources: Sources, mocker: MockerFixture) -> None:
    """
    must not do anything in case if directories are the same
    """
    walk_mock = mocker.patch("ahriman.core.build_tools.sources.walk")
    sources.move(Path("/same"), Path("/same"))
    walk_mock.assert_not_called()


def test_patch_apply(sources: Sources, mocker: MockerFixture) -> None:
    """
    must apply patches if any
    """
    patch = PkgbuildPatch(None, "patch")
    check_output_mock = mocker.patch("ahriman.core.build_tools.sources.check_output")

    local = Path("local")
    sources.patch_apply(local, patch)
    check_output_mock.assert_called_once_with(
        *sources.git(), "apply", "--ignore-space-change", "--ignore-whitespace",
        cwd=local, input_data=patch.value, logger=sources.logger
    )


def test_patch_apply_function(sources: Sources, mocker: MockerFixture) -> None:
    """
    must apply single-function patches
    """
    patch = PkgbuildPatch("version", "42")
    local = Path("local")
    write_mock = mocker.patch("ahriman.models.pkgbuild_patch.PkgbuildPatch.write")

    sources.patch_apply(local, patch)
    write_mock.assert_called_once_with(local / "PKGBUILD")
