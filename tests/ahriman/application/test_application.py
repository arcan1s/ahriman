import pytest

from pytest_mock import MockerFixture
from unittest import mock

from ahriman.application.application import Application
from ahriman.core.tree import Leaf, Tree
from ahriman.models.package import Package


def test_finalize(application: Application, mocker: MockerFixture) -> None:
    """
    must report and sync at the last
    """
    report_mock = mocker.patch("ahriman.application.application.Application.report")
    sync_mock = mocker.patch("ahriman.application.application.Application.sync")

    application._finalize([])
    report_mock.assert_called_once()
    sync_mock.assert_called_once()


def test_known_packages(application: Application, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must return not empty list of known packages
    """
    mocker.patch("ahriman.core.repository.repository.Repository.packages", return_value=[package_ahriman])
    packages = application._known_packages()
    assert len(packages) > 1
    assert package_ahriman.base in packages


def test_get_updates_all(application: Application, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must get updates for all
    """
    updates_aur_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_aur",
                                    return_value=[package_ahriman])
    updates_manual_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_manual")

    application.get_updates([], no_aur=False, no_manual=False, no_vcs=False, log_fn=print)
    updates_aur_mock.assert_called_with([], False)
    updates_manual_mock.assert_called_once()


def test_get_updates_disabled(application: Application, mocker: MockerFixture) -> None:
    """
    must get updates without anything
    """
    updates_aur_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_aur")
    updates_manual_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_manual")

    application.get_updates([], no_aur=True, no_manual=True, no_vcs=False, log_fn=print)
    updates_aur_mock.assert_not_called()
    updates_manual_mock.assert_not_called()


def test_get_updates_no_aur(application: Application, mocker: MockerFixture) -> None:
    """
    must get updates without aur
    """
    updates_aur_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_aur")
    updates_manual_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_manual")

    application.get_updates([], no_aur=True, no_manual=False, no_vcs=False, log_fn=print)
    updates_aur_mock.assert_not_called()
    updates_manual_mock.assert_called_once()


def test_get_updates_no_manual(application: Application, mocker: MockerFixture) -> None:
    """
    must get updates without manual
    """
    updates_aur_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_aur")
    updates_manual_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_manual")

    application.get_updates([], no_aur=False, no_manual=True, no_vcs=False, log_fn=print)
    updates_aur_mock.assert_called_with([], False)
    updates_manual_mock.assert_not_called()


def test_get_updates_no_vcs(application: Application, mocker: MockerFixture) -> None:
    """
    must get updates without VCS
    """
    updates_aur_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_aur")
    updates_manual_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_manual")

    application.get_updates([], no_aur=False, no_manual=False, no_vcs=True, log_fn=print)
    updates_aur_mock.assert_called_with([], True)
    updates_manual_mock.assert_called_once()


def test_get_updates_with_filter(application: Application, mocker: MockerFixture) -> None:
    """
    must get updates without VCS
    """
    updates_aur_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_aur")
    updates_manual_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_manual")

    application.get_updates(["filter"], no_aur=False, no_manual=False, no_vcs=False, log_fn=print)
    updates_aur_mock.assert_called_with(["filter"], False)
    updates_manual_mock.assert_called_once()


def test_add_directory(application: Application, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must add packages from directory
    """
    mocker.patch("ahriman.application.application.Application._known_packages", return_value=set())
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    iterdir_mock = mocker.patch("pathlib.Path.iterdir",
                                return_value=[package.filepath for package in package_ahriman.packages.values()])
    move_mock = mocker.patch("shutil.move")

    application.add([package_ahriman.base], False)
    iterdir_mock.assert_called_once()
    move_mock.assert_called_once()


def test_add_manual(application: Application, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must add package from AUR
    """
    mocker.patch("ahriman.application.application.Application._known_packages", return_value=set())
    mocker.patch("ahriman.models.package.Package.load", return_value=package_ahriman)
    fetch_mock = mocker.patch("ahriman.core.build_tools.task.Task.fetch")

    application.add([package_ahriman.base], True)
    fetch_mock.assert_called_once()


def test_add_manual_with_dependencies(application: Application, package_ahriman: Package,
                                      mocker: MockerFixture) -> None:
    """
    must add package from AUR with dependencies
    """
    mocker.patch("ahriman.application.application.Application._known_packages", return_value=set())
    mocker.patch("ahriman.models.package.Package.load", return_value=package_ahriman)
    mocker.patch("ahriman.core.build_tools.task.Task.fetch")
    dependencies_mock = mocker.patch("ahriman.models.package.Package.dependencies")

    application.add([package_ahriman.base], False)
    dependencies_mock.assert_called_once()


def test_add_package(application: Application, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must add package from archive
    """
    mocker.patch("ahriman.application.application.Application._known_packages", return_value=set())
    mocker.patch("pathlib.Path.is_file", return_value=True)
    move_mock = mocker.patch("shutil.move")

    application.add([package_ahriman.base], False)
    move_mock.assert_called_once()


def test_clean_build(application: Application, mocker: MockerFixture) -> None:
    """
    must clean build directory
    """
    clear_mock = mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_build")
    application.clean(False, True, True, True, True)
    clear_mock.assert_called_once()


def test_clean_cache(application: Application, mocker: MockerFixture) -> None:
    """
    must clean cache directory
    """
    clear_mock = mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_cache")
    application.clean(True, False, True, True, True)
    clear_mock.assert_called_once()


def test_clean_chroot(application: Application, mocker: MockerFixture) -> None:
    """
    must clean chroot directory
    """
    clear_mock = mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_chroot")
    application.clean(True, True, False, True, True)
    clear_mock.assert_called_once()


def test_clean_manual(application: Application, mocker: MockerFixture) -> None:
    """
    must clean manual directory
    """
    clear_mock = mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_manual")
    application.clean(True, True, True, False, True)
    clear_mock.assert_called_once()


def test_clean_packages(application: Application, mocker: MockerFixture) -> None:
    """
    must clean packages directory
    """
    clear_mock = mocker.patch("ahriman.core.repository.cleaner.Cleaner.clear_packages")
    application.clean(True, True, True, True, False)
    clear_mock.assert_called_once()


def test_remove(application: Application, mocker: MockerFixture) -> None:
    """
    must remove package
    """
    executor_mock = mocker.patch("ahriman.core.repository.executor.Executor.process_remove")
    finalize_mock = mocker.patch("ahriman.application.application.Application._finalize")

    application.remove([])
    executor_mock.assert_called_once()
    finalize_mock.assert_called_once()


def test_report(application: Application, mocker: MockerFixture) -> None:
    """
    must generate report
    """
    executor_mock = mocker.patch("ahriman.core.repository.executor.Executor.process_report")
    application.report([], [])
    executor_mock.assert_called_once()


def test_sign(application: Application, package_ahriman: Package, package_python_schedule: Package,
              mocker: MockerFixture) -> None:
    """
    must sign world
    """
    mocker.patch("ahriman.core.repository.repository.Repository.packages",
                 return_value=[package_ahriman, package_python_schedule])
    copy_mock = mocker.patch("shutil.copy")
    update_mock = mocker.patch("ahriman.application.application.Application.update")
    sign_repository_mock = mocker.patch("ahriman.core.sign.gpg.GPG.sign_repository")
    finalize_mock = mocker.patch("ahriman.application.application.Application._finalize")

    application.sign([])
    copy_mock.assert_has_calls([
        mock.call(pytest.helpers.anyvar(str), pytest.helpers.anyvar(str)),
        mock.call(pytest.helpers.anyvar(str), pytest.helpers.anyvar(str))
    ])
    update_mock.assert_called_with([])
    sign_repository_mock.assert_called_once()
    finalize_mock.assert_called_once()


def test_sign_skip(application: Application, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must skip sign packages with empty filename
    """
    package_ahriman.packages[package_ahriman.base].filename = None
    mocker.patch("ahriman.core.repository.repository.Repository.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.application.application.Application.update")

    application.sign([])


def test_sign_specific(application: Application, package_ahriman: Package, package_python_schedule: Package,
                       mocker: MockerFixture) -> None:
    """
    must sign only specified packages
    """
    mocker.patch("ahriman.core.repository.repository.Repository.packages",
                 return_value=[package_ahriman, package_python_schedule])
    copy_mock = mocker.patch("shutil.copy")
    update_mock = mocker.patch("ahriman.application.application.Application.update")
    sign_repository_mock = mocker.patch("ahriman.core.sign.gpg.GPG.sign_repository")
    finalize_mock = mocker.patch("ahriman.application.application.Application._finalize")

    application.sign([package_ahriman.base])
    copy_mock.assert_called_once()
    update_mock.assert_called_with([])
    sign_repository_mock.assert_called_once()
    finalize_mock.assert_called_once()


def test_sync(application: Application, mocker: MockerFixture) -> None:
    """
    must sync to remote
    """
    executor_mock = mocker.patch("ahriman.core.repository.executor.Executor.process_sync")
    application.sync([], [])
    executor_mock.assert_called_once()


def test_update(application: Application, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must process package updates
    """
    paths = [package.filepath for package in package_ahriman.packages.values()]
    tree = Tree([Leaf(package_ahriman, set())])

    mocker.patch("ahriman.core.tree.Tree.load", return_value=tree)
    mocker.patch("ahriman.core.repository.repository.Repository.packages_built", return_value=[])
    mocker.patch("ahriman.models.package.Package.load", return_value=package_ahriman)
    build_mock = mocker.patch("ahriman.core.repository.executor.Executor.process_build", return_value=paths)
    update_mock = mocker.patch("ahriman.core.repository.executor.Executor.process_update")
    finalize_mock = mocker.patch("ahriman.application.application.Application._finalize")

    application.update([package_ahriman])
    build_mock.assert_called_once()
    update_mock.assert_has_calls([mock.call([]), mock.call(paths)])
    finalize_mock.assert_has_calls([mock.call([]), mock.call([package_ahriman])])
