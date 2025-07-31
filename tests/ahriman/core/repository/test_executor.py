import pytest

from dataclasses import replace
from pathlib import Path
from pytest_mock import MockerFixture
from typing import Any
from unittest.mock import call as MockCall

from ahriman.core.repository.executor import Executor
from ahriman.models.changes import Changes
from ahriman.models.dependencies import Dependencies
from ahriman.models.package import Package
from ahriman.models.packagers import Packagers
from ahriman.models.user import User


def test_archive_lookup(executor: Executor, package_ahriman: Package, package_python_schedule: Package,
                        mocker: MockerFixture) -> None:
    """
    must existing packages which match the version
    """
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.preserve_owner")
    mocker.patch("pathlib.Path.iterdir", return_value=[
        Path("1.pkg.tar.zst"),
        Path("2.pkg.tar.zst"),
        Path("3.pkg.tar.zst"),
    ])
    mocker.patch("ahriman.models.package.Package.from_archive", side_effect=[
        package_ahriman,
        package_python_schedule,
        replace(package_ahriman, version="1"),
    ])
    glob_mock = mocker.patch("pathlib.Path.glob", return_value=[Path("1.pkg.tar.xz")])

    assert list(executor._archive_lookup(package_ahriman)) == [Path("1.pkg.tar.xz")]
    glob_mock.assert_called_once_with(f"{package_ahriman.packages[package_ahriman.base].filename}*")


def test_archive_lookup_version_mismatch(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return nothing if no packages found with the same version
    """
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.preserve_owner")
    mocker.patch("pathlib.Path.iterdir", return_value=[
        Path("1.pkg.tar.zst"),
    ])
    mocker.patch("ahriman.models.package.Package.from_archive", return_value=replace(package_ahriman, version="1"))

    assert list(executor._archive_lookup(package_ahriman)) == []


def test_archive_lookup_architecture_mismatch(executor: Executor, package_ahriman: Package,
                                              mocker: MockerFixture) -> None:
    """
    must return nothing if architecture doesn't match
    """
    package_ahriman.packages[package_ahriman.base].architecture = "x86_64"
    mocker.patch("ahriman.core.repository.executor.Executor.architecture", return_value="i686")
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.preserve_owner")
    mocker.patch("pathlib.Path.iterdir", return_value=[
        Path("1.pkg.tar.zst"),
    ])
    mocker.patch("ahriman.models.package.Package.from_archive", return_value=package_ahriman)

    assert list(executor._archive_lookup(package_ahriman)) == []


def test_archive_rename(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must correctly remove package archive
    """
    path = "gconf-3.2.6+11+g07808097-10-x86_64.pkg.tar.zst"
    safe_path = "gconf-3.2.6-11-g07808097-10-x86_64.pkg.tar.zst"
    package_ahriman.packages[package_ahriman.base].filename = path
    rename_mock = mocker.patch("ahriman.core.repository.executor.atomic_move")

    executor._archive_rename(package_ahriman.packages[package_ahriman.base], package_ahriman.base)
    rename_mock.assert_called_once_with(executor.paths.packages / path, executor.paths.packages / safe_path)
    assert package_ahriman.packages[package_ahriman.base].filename == safe_path


def test_archive_rename_empty_filename(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must skip renaming if filename is not set
    """
    package_ahriman.packages[package_ahriman.base].filename = None
    rename_mock = mocker.patch("ahriman.core.repository.executor.atomic_move")

    executor._archive_rename(package_ahriman.packages[package_ahriman.base], package_ahriman.base)
    rename_mock.assert_not_called()


def test_package_build(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must build single package
    """
    mocker.patch("ahriman.core.build_tools.task.Task.build", return_value=[Path(package_ahriman.base)])
    status_client_mock = mocker.patch("ahriman.core.status.Client.set_building")
    init_mock = mocker.patch("ahriman.core.build_tools.task.Task.init", return_value="sha")
    package_mock = mocker.patch("ahriman.models.package.Package.from_build", return_value=package_ahriman)
    lookup_mock = mocker.patch("ahriman.core.repository.executor.Executor._archive_lookup", return_value=[])
    with_packages_mock = mocker.patch("ahriman.models.package.Package.with_packages")
    rename_mock = mocker.patch("ahriman.core.repository.executor.atomic_move")

    assert executor._package_build(package_ahriman, Path("local"), "packager", None) == "sha"
    status_client_mock.assert_called_once_with(package_ahriman.base)
    init_mock.assert_called_once_with(pytest.helpers.anyvar(int), pytest.helpers.anyvar(int), None)
    package_mock.assert_called_once_with(Path("local"), executor.architecture, None)
    lookup_mock.assert_called_once_with(package_ahriman)
    with_packages_mock.assert_called_once_with([Path(package_ahriman.base)], executor.pacman)
    rename_mock.assert_called_once_with(Path(package_ahriman.base), executor.paths.packages / package_ahriman.base)


def test_package_build_copy(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must copy package from archive if there are already built ones
    """
    path = package_ahriman.packages[package_ahriman.base].filepath
    mocker.patch("ahriman.core.build_tools.task.Task.build", return_value=[Path(package_ahriman.base)])
    mocker.patch("ahriman.core.build_tools.task.Task.init")
    mocker.patch("ahriman.models.package.Package.from_build", return_value=package_ahriman)
    mocker.patch("ahriman.core.repository.executor.Executor._archive_lookup", return_value=[path])
    mocker.patch("ahriman.core.repository.executor.atomic_move")
    mocker.patch("ahriman.models.package.Package.with_packages")
    copy_mock = mocker.patch("shutil.copy")
    rename_mock = mocker.patch("ahriman.core.repository.executor.atomic_move")

    executor._package_build(package_ahriman, Path("local"), "packager", None)
    copy_mock.assert_called_once_with(path, Path("local"))
    rename_mock.assert_called_once_with(Path("local") / path, executor.paths.packages / path)


def test_package_remove(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must run remove for packages
    """
    repo_remove_mock = mocker.patch("ahriman.core.alpm.repo.Repo.remove")
    executor._package_remove(package_ahriman.base, package_ahriman.packages[package_ahriman.base].filepath)
    repo_remove_mock.assert_called_once_with(
        package_ahriman.base, package_ahriman.packages[package_ahriman.base].filepath)


def test_package_remove_failed(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must suppress errors during archive removal
    """
    mocker.patch("ahriman.core.alpm.repo.Repo.remove", side_effect=Exception)
    executor._package_remove(package_ahriman.base, package_ahriman.packages[package_ahriman.base].filepath)


def test_package_remove_base(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must run remove base from status client
    """
    status_client_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_remove")
    executor._package_remove_base(package_ahriman.base)
    status_client_mock.assert_called_once_with(package_ahriman.base)


def test_package_remove_base_failed(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must suppress errors during base removal
    """
    mocker.patch("ahriman.core.status.local_client.LocalClient.package_remove", side_effect=Exception)
    executor._package_remove_base(package_ahriman.base)


def test_package_update(executor: Executor, package_ahriman: Package, user: User, mocker: MockerFixture) -> None:
    """
    must update built package in repository
    """
    rename_mock = mocker.patch("ahriman.core.repository.executor.atomic_move")
    symlink_mock = mocker.patch("pathlib.Path.symlink_to")
    repo_add_mock = mocker.patch("ahriman.core.alpm.repo.Repo.add")
    sign_package_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process_sign_package", side_effect=lambda fn, _: [fn])
    filepath = next(package.filepath for package in package_ahriman.packages.values())

    executor._package_update(filepath, package_ahriman.base, user.key)
    # must move files (once)
    rename_mock.assert_called_once_with(
        executor.paths.packages / filepath, executor.paths.archive_for(package_ahriman.base) / filepath)
    # must sign package
    sign_package_mock.assert_called_once_with(executor.paths.packages / filepath, user.key)
    # symlink to the archive
    symlink_mock.assert_called_once_with(
        Path("..") /
        ".." /
        ".." /
        executor.paths.archive_for(
            package_ahriman.base).relative_to(
            executor.paths.root) /
        filepath)
    # must add package
    repo_add_mock.assert_called_once_with(executor.paths.repository / filepath)


def test_package_update_empty_filename(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must skip update for package which does not have path
    """
    rename_mock = mocker.patch("ahriman.core.repository.executor.atomic_move")
    executor._package_update(None, package_ahriman.base, None)
    rename_mock.assert_not_called()


def test_process_build(executor: Executor, package_ahriman: Package, passwd: Any, mocker: MockerFixture) -> None:
    """
    must run build process
    """
    mocker.patch("ahriman.models.repository_paths.getpwuid", return_value=passwd)
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[package_ahriman])
    changes_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_changes_get",
                                return_value=Changes("commit", "change"))
    commit_sha_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_changes_update")
    depends_on_mock = mocker.patch("ahriman.core.build_tools.package_archive.PackageArchive.depends_on",
                                   return_value=Dependencies())
    dependencies_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_dependencies_update")
    build_mock = mocker.patch("ahriman.core.repository.executor.Executor._package_build", return_value="sha")

    executor.process_build([package_ahriman], Packagers("packager"), bump_pkgrel=False)
    changes_mock.assert_called_once_with(package_ahriman.base)
    build_mock.assert_called_once_with(package_ahriman, pytest.helpers.anyvar(Path, strict=True), None, None)
    depends_on_mock.assert_called_once_with()
    dependencies_mock.assert_called_once_with(package_ahriman.base, Dependencies())
    commit_sha_mock.assert_called_once_with(package_ahriman.base, Changes("sha", "change"))


def test_process_build_bump_pkgrel(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must run build process and pass current package version to build tools
    """
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.core.build_tools.task.Task.build", return_value=[Path(package_ahriman.base)])
    mocker.patch("ahriman.core.repository.executor.atomic_move")
    init_mock = mocker.patch("ahriman.core.build_tools.task.Task.init")

    executor.process_build([package_ahriman], Packagers("packager"), bump_pkgrel=True)
    init_mock.assert_called_once_with(pytest.helpers.anyvar(int),
                                      pytest.helpers.anyvar(int),
                                      package_ahriman.version)


def test_process_build_failure(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must run correct process failed builds
    """
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.core.repository.executor.Executor.packages_built")
    mocker.patch("ahriman.core.build_tools.task.Task.build", return_value=[Path(package_ahriman.base)])
    mocker.patch("ahriman.core.build_tools.task.Task.init")
    mocker.patch("ahriman.core.repository.executor.atomic_move", side_effect=Exception)
    status_client_mock = mocker.patch("ahriman.core.status.Client.set_failed")

    executor.process_build([package_ahriman])
    status_client_mock.assert_called_once_with(package_ahriman.base)


def test_process_remove_base(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must run remove process for whole base
    """
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[package_ahriman])
    remove_mock = mocker.patch("ahriman.core.repository.executor.Executor._package_remove")
    base_remove_mock = mocker.patch("ahriman.core.repository.executor.Executor._package_remove_base")

    executor.process_remove([package_ahriman.base])
    # must remove via alpm wrapper
    remove_mock.assert_called_once_with(
        package_ahriman.base, package_ahriman.packages[package_ahriman.base].filepath)
    # must update status and remove package files
    base_remove_mock.assert_called_once_with(package_ahriman.base)


def test_process_remove_with_debug(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must run remove debug packages too
    """
    package_ahriman.packages = {
        package_ahriman.base: package_ahriman.packages[package_ahriman.base],
        f"{package_ahriman.base}-debug": package_ahriman.packages[package_ahriman.base],
    }
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.core.repository.executor.Executor._package_remove_base")
    remove_mock = mocker.patch("ahriman.core.repository.executor.Executor._package_remove")

    executor.process_remove([package_ahriman.base])
    # must remove via alpm wrapper
    remove_mock.assert_has_calls([
        MockCall(package_ahriman.base, package_ahriman.packages[package_ahriman.base].filepath),
        MockCall(f"{package_ahriman.base}-debug", package_ahriman.packages[package_ahriman.base].filepath),
    ])


def test_process_remove_base_multiple(executor: Executor, package_python_schedule: Package,
                                      mocker: MockerFixture) -> None:
    """
    must run remove process for whole base with multiple packages
    """
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[package_python_schedule])
    remove_mock = mocker.patch("ahriman.core.repository.executor.Executor._package_remove")
    status_client_mock = mocker.patch("ahriman.core.repository.executor.Executor._package_remove_base")

    executor.process_remove([package_python_schedule.base])
    # must remove via alpm wrapper
    remove_mock.assert_has_calls([
        MockCall(package, props.filepath)
        for package, props in package_python_schedule.packages.items()
    ], any_order=True)
    # must update status
    status_client_mock.assert_called_once_with(package_python_schedule.base)


def test_process_remove_base_single(executor: Executor, package_python_schedule: Package,
                                    mocker: MockerFixture) -> None:
    """
    must run remove process for single package in base
    """
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[package_python_schedule])
    remove_mock = mocker.patch("ahriman.core.repository.executor.Executor._package_remove")
    status_client_mock = mocker.patch("ahriman.core.repository.executor.Executor._package_remove_base")

    executor.process_remove(["python2-schedule"])
    # must remove via alpm wrapper
    remove_mock.assert_called_once_with(
        "python2-schedule", package_python_schedule.packages["python2-schedule"].filepath)
    # must not update status
    status_client_mock.assert_not_called()


def test_process_remove_nothing(executor: Executor, package_ahriman: Package, package_python_schedule: Package,
                                mocker: MockerFixture) -> None:
    """
    must not remove anything if it was not requested
    """
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[package_ahriman])
    remove_mock = mocker.patch("ahriman.core.repository.executor.Executor._package_remove")

    executor.process_remove([package_python_schedule.base])
    remove_mock.assert_not_called()


def test_process_remove_unknown(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must remove unknown package base
    """
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[])
    remove_mock = mocker.patch("ahriman.core.repository.executor.Executor._package_remove")
    status_client_mock = mocker.patch("ahriman.core.repository.executor.Executor._package_remove_base")

    executor.process_remove([package_ahriman.base])
    remove_mock.assert_not_called()
    status_client_mock.assert_called_once_with(package_ahriman.base)


def test_process_update(executor: Executor, package_ahriman: Package, user: User, mocker: MockerFixture) -> None:
    """
    must run update process
    """
    mocker.patch("ahriman.core.repository.executor.Executor.load_archives", return_value=[package_ahriman])
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[package_ahriman])
    rename_mock = mocker.patch("ahriman.core.repository.executor.Executor._archive_rename")
    update_mock = mocker.patch("ahriman.core.repository.executor.Executor._package_update")
    status_client_mock = mocker.patch("ahriman.core.status.Client.set_success")
    remove_mock = mocker.patch("ahriman.core.repository.executor.Executor.process_remove")
    packager_mock = mocker.patch("ahriman.core.repository.executor.Executor.packager", return_value=user)
    filepath = next(package.filepath for package in package_ahriman.packages.values())

    # must return complete
    assert executor.process_update([filepath], Packagers("packager"))
    packager_mock.assert_called_once_with(Packagers("packager"), "ahriman")
    rename_mock.assert_called_once_with(package_ahriman.packages[package_ahriman.base], package_ahriman.base)
    update_mock.assert_called_once_with(filepath.name, package_ahriman.base, user.key)
    # must update status
    status_client_mock.assert_called_once_with(package_ahriman)
    # must clear directory
    from ahriman.core.repository.cleaner import Cleaner
    Cleaner.clear_packages.assert_called_once_with()
    # clear removed packages
    remove_mock.assert_called_once_with([])


def test_process_update_group(executor: Executor, package_python_schedule: Package,
                              mocker: MockerFixture) -> None:
    """
    must group single packages under one base
    """
    mocker.patch("ahriman.core.repository.executor.Executor.load_archives", return_value=[package_python_schedule])
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[package_python_schedule])
    update_mock = mocker.patch("ahriman.core.repository.executor.Executor._package_update")
    status_client_mock = mocker.patch("ahriman.core.status.Client.set_success")
    remove_mock = mocker.patch("ahriman.core.repository.executor.Executor.process_remove")

    executor.process_update([package.filepath for package in package_python_schedule.packages.values()])
    update_mock.assert_has_calls([
        MockCall(package.filename, package_python_schedule.base, None)
        for package in package_python_schedule.packages.values()
    ], any_order=True)
    status_client_mock.assert_called_once_with(package_python_schedule)
    remove_mock.assert_called_once_with([])


def test_process_update_failed(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must process update for failed package
    """
    mocker.patch("ahriman.core.repository.executor.Executor._package_update", side_effect=Exception)
    mocker.patch("ahriman.core.repository.executor.Executor.load_archives", return_value=[package_ahriman])
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[package_ahriman])
    status_client_mock = mocker.patch("ahriman.core.status.Client.set_failed")

    executor.process_update([package.filepath for package in package_ahriman.packages.values()])
    status_client_mock.assert_called_once_with(package_ahriman.base)


def test_process_update_removed_package(executor: Executor, package_python_schedule: Package,
                                        mocker: MockerFixture) -> None:
    """
    must remove packages which have been removed from the new base
    """
    without_python2 = Package.from_json(package_python_schedule.view())
    del without_python2.packages["python2-schedule"]

    mocker.patch("ahriman.core.repository.executor.Executor._package_update")
    mocker.patch("ahriman.core.repository.executor.Executor.load_archives", return_value=[without_python2])
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[package_python_schedule])
    remove_mock = mocker.patch("ahriman.core.repository.executor.Executor.process_remove")

    executor.process_update([package.filepath for package in without_python2.packages.values()])
    remove_mock.assert_called_once_with(["python2-schedule"])
