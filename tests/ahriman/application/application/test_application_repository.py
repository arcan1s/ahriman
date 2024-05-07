import pytest

from pytest_mock import MockerFixture
from unittest.mock import call as MockCall

from ahriman.application.application.application_repository import ApplicationRepository
from ahriman.core.tree import Leaf, Tree
from ahriman.models.changes import Changes
from ahriman.models.package import Package
from ahriman.models.packagers import Packagers
from ahriman.models.result import Result


def test_changes(application_repository: ApplicationRepository, package_ahriman: Package,
                 mocker: MockerFixture) -> None:
    """
    must generate changes for the packages
    """
    changes = Changes("hash", "change")
    hashes_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_changes_get", return_value=changes)
    changes_mock = mocker.patch("ahriman.core.repository.Repository.package_changes", return_value=changes)
    report_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_changes_update")

    application_repository.changes([package_ahriman])
    hashes_mock.assert_called_once_with(package_ahriman.base)
    changes_mock.assert_called_once_with(package_ahriman, changes.last_commit_sha)
    report_mock.assert_called_once_with(package_ahriman.base, changes)


def test_changes_skip(application_repository: ApplicationRepository, package_ahriman: Package,
                      mocker: MockerFixture) -> None:
    """
    must skip change generation if no last commit sha has been found
    """
    changes_mock = mocker.patch("ahriman.core.repository.Repository.package_changes")
    report_mock = mocker.patch("ahriman.core.status.local_client.LocalClient.package_changes_update")

    application_repository.changes([package_ahriman])
    changes_mock.assert_not_called()
    report_mock.assert_not_called()


def test_clean_cache(application_repository: ApplicationRepository, mocker: MockerFixture) -> None:
    """
    must clean cache directory
    """
    clear_mock = mocker.patch("ahriman.core.repository.Repository.clear_cache")
    application_repository.clean(cache=True, chroot=False, manual=False, packages=False, pacman=False)
    clear_mock.assert_called_once_with()


def test_clean_chroot(application_repository: ApplicationRepository, mocker: MockerFixture) -> None:
    """
    must clean chroot directory
    """
    clear_mock = mocker.patch("ahriman.core.repository.Repository.clear_chroot")
    application_repository.clean(cache=False, chroot=True, manual=False, packages=False, pacman=False)
    clear_mock.assert_called_once_with()


def test_clean_manual(application_repository: ApplicationRepository, mocker: MockerFixture) -> None:
    """
    must clean manual directory
    """
    clear_mock = mocker.patch("ahriman.core.repository.Repository.clear_queue")
    application_repository.clean(cache=False, chroot=False, manual=True, packages=False, pacman=False)
    clear_mock.assert_called_once_with()


def test_clean_packages(application_repository: ApplicationRepository, mocker: MockerFixture) -> None:
    """
    must clean packages directory
    """
    clear_mock = mocker.patch("ahriman.core.repository.Repository.clear_packages")
    application_repository.clean(cache=False, chroot=False, manual=False, packages=True, pacman=False)
    clear_mock.assert_called_once_with()


def test_clean_pacman(application_repository: ApplicationRepository, mocker: MockerFixture) -> None:
    """
    must clean packages directory
    """
    clear_mock = mocker.patch("ahriman.core.repository.Repository.clear_pacman")
    application_repository.clean(cache=False, chroot=False, manual=False, packages=False, pacman=True)
    clear_mock.assert_called_once_with()


def test_on_result(application_repository: ApplicationRepository) -> None:
    """
    must raise NotImplemented for missing finalize method
    """
    with pytest.raises(NotImplementedError):
        application_repository.on_result(Result())


def test_sign(application_repository: ApplicationRepository, package_ahriman: Package, package_python_schedule: Package,
              mocker: MockerFixture) -> None:
    """
    must sign world
    """
    mocker.patch("ahriman.core.repository.repository.Repository.packages",
                 return_value=[package_ahriman, package_python_schedule])
    sign_package_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process_sign_package")
    sign_repository_mock = mocker.patch("ahriman.core.sign.gpg.GPG.process_sign_repository")
    on_result_mock = mocker.patch(
        "ahriman.application.application.application_repository.ApplicationRepository.on_result")

    application_repository.sign([])
    sign_package_mock.assert_has_calls([
        MockCall(pytest.helpers.anyvar(int), None),
        MockCall(pytest.helpers.anyvar(int), None),
        MockCall(pytest.helpers.anyvar(int), None),
    ])
    sign_repository_mock.assert_called_once_with(application_repository.repository.repo.repo_path)
    on_result_mock.assert_called_once_with(Result())


def test_sign_skip(application_repository: ApplicationRepository, package_ahriman: Package,
                   mocker: MockerFixture) -> None:
    """
    must skip sign packages with empty filename
    """
    package_ahriman.packages[package_ahriman.base].filename = None
    mocker.patch("ahriman.core.repository.repository.Repository.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.application.application.application_repository.ApplicationRepository.update")
    mocker.patch("ahriman.application.application.application_repository.ApplicationRepository.on_result")

    application_repository.sign([])


def test_unknown_no_aur(application_repository: ApplicationRepository, package_ahriman: Package,
                        mocker: MockerFixture) -> None:
    """
    must return empty list in case if there is locally stored PKGBUILD
    """
    mocker.patch("ahriman.core.repository.repository.Repository.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.models.package.Package.from_aur", side_effect=Exception())
    mocker.patch("ahriman.models.package.Package.from_build", return_value=package_ahriman)
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("ahriman.core.build_tools.sources.Sources.has_remotes", return_value=False)

    assert not application_repository.unknown()


def test_unknown_no_aur_no_local(application_repository: ApplicationRepository, package_ahriman: Package,
                                 mocker: MockerFixture) -> None:
    """
    must return list of packages missing in aur and in local storage
    """
    mocker.patch("ahriman.core.repository.repository.Repository.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.models.package.Package.from_aur", side_effect=Exception())
    mocker.patch("pathlib.Path.is_dir", return_value=False)

    packages = application_repository.unknown()
    assert packages == list(package_ahriman.packages.keys())


def test_unknown_no_local(application_repository: ApplicationRepository, package_ahriman: Package,
                          mocker: MockerFixture) -> None:
    """
    must return empty list in case if there is package in AUR
    """
    mocker.patch("ahriman.core.repository.repository.Repository.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.models.package.Package.from_aur")
    mocker.patch("pathlib.Path.is_dir", return_value=False)

    assert not application_repository.unknown()


def test_update(application_repository: ApplicationRepository, package_ahriman: Package, result: Result,
                mocker: MockerFixture) -> None:
    """
    must process package updates
    """
    paths = [package.filepath for package in package_ahriman.packages.values()]
    tree = Tree([Leaf(package_ahriman)])

    resolve_mock = mocker.patch("ahriman.application.application.workers.local_updater.LocalUpdater.partition",
                                return_value=tree.levels())
    mocker.patch("ahriman.core.repository.repository.Repository.packages_built", return_value=paths)
    build_mock = mocker.patch("ahriman.application.application.workers.local_updater.LocalUpdater.update",
                              return_value=result)
    update_mock = mocker.patch("ahriman.core.repository.Repository.process_update", return_value=result)
    on_result_mock = mocker.patch(
        "ahriman.application.application.application_repository.ApplicationRepository.on_result")

    application_repository.update([package_ahriman], Packagers("username"), bump_pkgrel=True)
    resolve_mock.assert_called_once_with([package_ahriman])
    build_mock.assert_called_once_with([package_ahriman], Packagers("username"), bump_pkgrel=True)
    update_mock.assert_called_once_with(paths, Packagers("username"))
    on_result_mock.assert_has_calls([MockCall(result), MockCall(result)])


def test_update_empty(application_repository: ApplicationRepository, package_ahriman: Package, result: Result,
                      mocker: MockerFixture) -> None:
    """
    must skip updating repository if no packages supplied
    """
    tree = Tree([Leaf(package_ahriman)])

    mocker.patch("ahriman.application.application.workers.Updater.partition", return_value=tree.levels())
    mocker.patch("ahriman.core.repository.Repository.packages_built", return_value=[])
    mocker.patch("ahriman.application.application.workers.local_updater.LocalUpdater.update", return_value=result)
    mocker.patch("ahriman.application.application.application_repository.ApplicationRepository.on_result")
    update_mock = mocker.patch("ahriman.core.repository.Repository.process_update")

    application_repository.update([package_ahriman])
    update_mock.assert_not_called()


def test_updates_all(application_repository: ApplicationRepository, package_ahriman: Package,
                     mocker: MockerFixture) -> None:
    """
    must get updates for all
    """
    updates_aur_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_aur",
                                    return_value=[package_ahriman])
    updates_local_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_local")
    updates_manual_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_manual")
    updates_deps_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_dependencies")

    application_repository.updates([], aur=True, local=True, manual=True, vcs=True, check_files=True)
    updates_aur_mock.assert_called_once_with([], vcs=True)
    updates_local_mock.assert_called_once_with(vcs=True)
    updates_manual_mock.assert_called_once_with()
    updates_deps_mock.assert_called_once_with([])


def test_updates_disabled(application_repository: ApplicationRepository, mocker: MockerFixture) -> None:
    """
    must get updates without anything
    """
    updates_aur_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_aur")
    updates_local_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_local")
    updates_manual_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_manual")
    updates_deps_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_dependencies")

    application_repository.updates([], aur=False, local=False, manual=False, vcs=True, check_files=False)
    updates_aur_mock.assert_not_called()
    updates_local_mock.assert_not_called()
    updates_manual_mock.assert_not_called()
    updates_deps_mock.assert_not_called()


def test_updates_no_aur(application_repository: ApplicationRepository, mocker: MockerFixture) -> None:
    """
    must get updates without aur
    """
    updates_aur_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_aur")
    updates_local_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_local")
    updates_manual_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_manual")
    updates_deps_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_dependencies")

    application_repository.updates([], aur=False, local=True, manual=True, vcs=True, check_files=True)
    updates_aur_mock.assert_not_called()
    updates_local_mock.assert_called_once_with(vcs=True)
    updates_manual_mock.assert_called_once_with()
    updates_deps_mock.assert_called_once_with([])


def test_updates_no_local(application_repository: ApplicationRepository, mocker: MockerFixture) -> None:
    """
    must get updates without local packages
    """
    updates_aur_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_aur")
    updates_local_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_local")
    updates_manual_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_manual")
    updates_deps_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_dependencies")

    application_repository.updates([], aur=True, local=False, manual=True, vcs=True, check_files=True)
    updates_aur_mock.assert_called_once_with([], vcs=True)
    updates_local_mock.assert_not_called()
    updates_manual_mock.assert_called_once_with()
    updates_deps_mock.assert_called_once_with([])


def test_updates_no_manual(application_repository: ApplicationRepository, mocker: MockerFixture) -> None:
    """
    must get updates without manual
    """
    updates_aur_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_aur")
    updates_local_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_local")
    updates_manual_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_manual")
    updates_deps_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_dependencies")

    application_repository.updates([], aur=True, local=True, manual=False, vcs=True, check_files=True)
    updates_aur_mock.assert_called_once_with([], vcs=True)
    updates_local_mock.assert_called_once_with(vcs=True)
    updates_manual_mock.assert_not_called()
    updates_deps_mock.assert_called_once_with([])


def test_updates_no_vcs(application_repository: ApplicationRepository, mocker: MockerFixture) -> None:
    """
    must get updates without VCS
    """
    updates_aur_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_aur")
    updates_local_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_local")
    updates_manual_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_manual")
    updates_deps_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_dependencies")

    application_repository.updates([], aur=True, local=True, manual=True, vcs=False, check_files=True)
    updates_aur_mock.assert_called_once_with([], vcs=False)
    updates_local_mock.assert_called_once_with(vcs=False)
    updates_manual_mock.assert_called_once_with()
    updates_deps_mock.assert_called_once_with([])


def test_updates_no_check_files(application_repository: ApplicationRepository, mocker: MockerFixture) -> None:
    """
    must get updates without checking broken links
    """
    updates_aur_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_aur")
    updates_local_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_local")
    updates_manual_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_manual")
    updates_deps_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_dependencies")

    application_repository.updates([], aur=True, local=True, manual=True, vcs=True, check_files=False)
    updates_aur_mock.assert_called_once_with([], vcs=True)
    updates_local_mock.assert_called_once_with(vcs=True)
    updates_manual_mock.assert_called_once_with()
    updates_deps_mock.assert_not_called()


def test_updates_with_filter(application_repository: ApplicationRepository, mocker: MockerFixture) -> None:
    """
    must get updates with filter
    """
    updates_aur_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_aur")
    updates_local_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_local")
    updates_manual_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_manual")
    updates_deps_mock = mocker.patch("ahriman.core.repository.update_handler.UpdateHandler.updates_dependencies")

    application_repository.updates(["filter"], aur=True, local=True, manual=True, vcs=True, check_files=True)
    updates_aur_mock.assert_called_once_with(["filter"], vcs=True)
    updates_local_mock.assert_called_once_with(vcs=True)
    updates_manual_mock.assert_called_once_with()
    updates_deps_mock.assert_called_once_with(["filter"])
