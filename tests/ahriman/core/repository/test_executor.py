import pytest

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


def test_process_build(executor: Executor, package_ahriman: Package, passwd: Any, mocker: MockerFixture) -> None:
    """
    must run build process
    """
    dependencies = Dependencies(package_ahriman.base)
    mocker.patch("ahriman.models.repository_paths.getpwuid", return_value=passwd)
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.core.build_tools.task.Task.build", return_value=[Path(package_ahriman.base)])
    init_mock = mocker.patch("ahriman.core.build_tools.task.Task.init", return_value="sha")
    move_mock = mocker.patch("shutil.move")
    status_client_mock = mocker.patch("ahriman.core.status.client.Client.set_building")
    commit_sha_mock = mocker.patch("ahriman.core.status.client.Client.package_changes_set")
    depends_on_mock = mocker.patch("ahriman.models.package_archive.PackageArchive.depends_on",
                                   return_value=dependencies)
    dependencies_mock = mocker.patch("ahriman.core.database.SQLite.dependencies_insert")

    executor.process_build([package_ahriman], Packagers("packager"), bump_pkgrel=False)
    init_mock.assert_called_once_with(pytest.helpers.anyvar(int), pytest.helpers.anyvar(int), None)
    depends_on_mock.assert_called_once_with()
    dependencies_mock.assert_called_once_with(dependencies)
    # must move files (once)
    move_mock.assert_called_once_with(Path(package_ahriman.base), executor.paths.packages / package_ahriman.base)
    # must update status
    status_client_mock.assert_called_once_with(package_ahriman.base)
    commit_sha_mock.assert_called_once_with(package_ahriman.base, Changes("sha"))


def test_process_build_bump_pkgrel(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must run build process and pass current package version to build tools
    """
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.core.build_tools.task.Task.build", return_value=[Path(package_ahriman.base)])
    mocker.patch("shutil.move")
    mocker.patch("ahriman.core.status.client.Client.set_building")
    mocker.patch("ahriman.core.status.client.Client.package_changes_set")
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
    mocker.patch("shutil.move", side_effect=Exception())
    status_client_mock = mocker.patch("ahriman.core.status.client.Client.set_failed")

    executor.process_build([package_ahriman])
    status_client_mock.assert_called_once_with(package_ahriman.base)


def test_process_remove_base(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must run remove process for whole base
    """
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[package_ahriman])
    tree_clear_mock = mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_clear")
    repo_remove_mock = mocker.patch("ahriman.core.alpm.repo.Repo.remove")
    database_mock = mocker.patch("ahriman.core.database.SQLite.package_clear")
    status_client_mock = mocker.patch("ahriman.core.status.client.Client.package_remove")

    executor.process_remove([package_ahriman.base])
    # must remove via alpm wrapper
    repo_remove_mock.assert_called_once_with(
        package_ahriman.base, package_ahriman.packages[package_ahriman.base].filepath)
    # must update status and remove package files
    tree_clear_mock.assert_called_once_with(package_ahriman.base)
    database_mock.assert_called_once_with(package_ahriman.base)
    status_client_mock.assert_called_once_with(package_ahriman.base)


def test_process_remove_base_multiple(executor: Executor, package_python_schedule: Package,
                                      mocker: MockerFixture) -> None:
    """
    must run remove process for whole base with multiple packages
    """
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[package_python_schedule])
    repo_remove_mock = mocker.patch("ahriman.core.alpm.repo.Repo.remove")
    status_client_mock = mocker.patch("ahriman.core.status.client.Client.package_remove")

    executor.process_remove([package_python_schedule.base])
    # must remove via alpm wrapper
    repo_remove_mock.assert_has_calls([
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
    repo_remove_mock = mocker.patch("ahriman.core.alpm.repo.Repo.remove")
    status_client_mock = mocker.patch("ahriman.core.status.client.Client.package_remove")

    executor.process_remove(["python2-schedule"])
    # must remove via alpm wrapper
    repo_remove_mock.assert_called_once_with(
        "python2-schedule", package_python_schedule.packages["python2-schedule"].filepath)
    # must not update status
    status_client_mock.assert_not_called()


def test_process_remove_failed(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must suppress tree clear errors during package base removal
    """
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.models.repository_paths.RepositoryPaths.tree_clear", side_effect=Exception())
    executor.process_remove([package_ahriman.base])


def test_process_remove_tree_clear_failed(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must suppress remove errors
    """
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.core.alpm.repo.Repo.remove", side_effect=Exception())
    executor.process_remove([package_ahriman.base])


def test_process_remove_nothing(executor: Executor, package_ahriman: Package, package_python_schedule: Package,
                                mocker: MockerFixture) -> None:
    """
    must not remove anything if it was not requested
    """
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[package_ahriman])
    repo_remove_mock = mocker.patch("ahriman.core.alpm.repo.Repo.remove")

    executor.process_remove([package_python_schedule.base])
    repo_remove_mock.assert_not_called()


def test_process_remove_unknown(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must remove unknown package base
    """
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[])
    repo_remove_mock = mocker.patch("ahriman.core.alpm.repo.Repo.remove")
    status_client_mock = mocker.patch("ahriman.core.status.client.Client.package_remove")

    executor.process_remove([package_ahriman.base])
    repo_remove_mock.assert_not_called()
    status_client_mock.assert_called_once_with(package_ahriman.base)


def test_process_update(executor: Executor, package_ahriman: Package, user: User, mocker: MockerFixture) -> None:
    """
    must run update process
    """
    mocker.patch("ahriman.core.repository.executor.Executor.load_archives", return_value=[package_ahriman])
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[package_ahriman])
    move_mock = mocker.patch("shutil.move")
    repo_add_mock = mocker.patch("ahriman.core.alpm.repo.Repo.add")
    sign_package_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process_sign_package", side_effect=lambda fn, _: [fn])
    status_client_mock = mocker.patch("ahriman.core.status.client.Client.set_success")
    remove_mock = mocker.patch("ahriman.core.repository.executor.Executor.process_remove")
    packager_mock = mocker.patch("ahriman.core.repository.executor.Executor.packager", return_value=user)
    filepath = next(package.filepath for package in package_ahriman.packages.values())

    # must return complete
    assert executor.process_update([filepath], Packagers("packager"))
    packager_mock.assert_called_once_with(Packagers("packager"), "ahriman")
    # must move files (once)
    move_mock.assert_called_once_with(executor.paths.packages / filepath, executor.paths.repository / filepath)
    # must sign package
    sign_package_mock.assert_called_once_with(executor.paths.packages / filepath, user.key)
    # must add package
    repo_add_mock.assert_called_once_with(executor.paths.repository / filepath)
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
    mocker.patch("shutil.move")
    mocker.patch("ahriman.core.repository.executor.Executor.load_archives", return_value=[package_python_schedule])
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[package_python_schedule])
    repo_add_mock = mocker.patch("ahriman.core.alpm.repo.Repo.add")
    status_client_mock = mocker.patch("ahriman.core.status.client.Client.set_success")
    remove_mock = mocker.patch("ahriman.core.repository.executor.Executor.process_remove")

    executor.process_update([package.filepath for package in package_python_schedule.packages.values()])
    repo_add_mock.assert_has_calls([
        MockCall(executor.paths.repository / package.filepath)
        for package in package_python_schedule.packages.values()
    ], any_order=True)
    status_client_mock.assert_called_once_with(package_python_schedule)
    remove_mock.assert_called_once_with([])


def test_process_update_unsafe(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must encode file name
    """
    path = "gconf-3.2.6+11+g07808097-10-x86_64.pkg.tar.zst"
    safe_path = "gconf-3.2.6-11-g07808097-10-x86_64.pkg.tar.zst"
    package_ahriman.packages[package_ahriman.base].filename = path

    mocker.patch("ahriman.core.repository.executor.Executor.load_archives", return_value=[package_ahriman])
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[package_ahriman])
    move_mock = mocker.patch("shutil.move")
    repo_add_mock = mocker.patch("ahriman.core.alpm.repo.Repo.add")

    executor.process_update([Path(path)])
    move_mock.assert_has_calls([
        MockCall(executor.paths.packages / path, executor.paths.packages / safe_path),
        MockCall(executor.paths.packages / safe_path, executor.paths.repository / safe_path)
    ])
    repo_add_mock.assert_called_once_with(executor.paths.repository / safe_path)


def test_process_empty_filename(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must skip update for package which does not have path
    """
    package_ahriman.packages[package_ahriman.base].filename = None
    mocker.patch("ahriman.core.repository.executor.Executor.load_archives", return_value=[package_ahriman])
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[package_ahriman])
    executor.process_update([package.filepath for package in package_ahriman.packages.values()])


def test_process_update_failed(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must process update for failed package
    """
    mocker.patch("shutil.move", side_effect=Exception())
    mocker.patch("ahriman.core.repository.executor.Executor.load_archives", return_value=[package_ahriman])
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[package_ahriman])
    status_client_mock = mocker.patch("ahriman.core.status.client.Client.set_failed")

    executor.process_update([package.filepath for package in package_ahriman.packages.values()])
    status_client_mock.assert_called_once_with(package_ahriman.base)


def test_process_update_removed_package(executor: Executor, package_python_schedule: Package,
                                        mocker: MockerFixture) -> None:
    """
    must remove packages which have been removed from the new base
    """
    without_python2 = Package.from_json(package_python_schedule.view())
    del without_python2.packages["python2-schedule"]

    mocker.patch("shutil.move")
    mocker.patch("ahriman.core.alpm.repo.Repo.add")
    mocker.patch("ahriman.core.repository.executor.Executor.load_archives", return_value=[without_python2])
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[package_python_schedule])
    remove_mock = mocker.patch("ahriman.core.repository.executor.Executor.process_remove")

    executor.process_update([package.filepath for package in without_python2.packages.values()])
    remove_mock.assert_called_once_with(["python2-schedule"])
