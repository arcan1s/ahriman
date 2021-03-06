import pytest

from pathlib import Path
from pytest_mock import MockerFixture
from unittest import mock

from ahriman.core.report.report import Report
from ahriman.core.repository.executor import Executor
from ahriman.core.upload.upload import Upload
from ahriman.models.package import Package


def test_packages(executor: Executor) -> None:
    """
    must raise NotImplemented for missing method
    """
    with pytest.raises(NotImplementedError):
        executor.packages()


def test_process_build(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must run build process
    """
    mocker.patch("ahriman.core.build_tools.task.Task.build", return_value=[Path(package_ahriman.base)])
    mocker.patch("ahriman.core.build_tools.task.Task.init")
    move_mock = mocker.patch("shutil.move")
    status_client_mock = mocker.patch("ahriman.core.status.client.Client.set_building")
    built_packages_mock = mocker.patch("ahriman.core.repository.executor.Executor.packages_built")

    executor.process_build([package_ahriman])
    # must move files (once)
    move_mock.assert_called_once()
    # must update status
    status_client_mock.assert_called_once()
    # must clear directory
    from ahriman.core.repository.cleaner import Cleaner
    Cleaner.clear_build.assert_called_once()
    # must return build packages after all
    built_packages_mock.assert_called_once()


def test_process_build_failure(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must run correct process failed builds
    """
    mocker.patch("ahriman.core.repository.executor.Executor.packages_built")
    mocker.patch("ahriman.core.build_tools.task.Task.build", return_value=[Path(package_ahriman.base)])
    mocker.patch("ahriman.core.build_tools.task.Task.init")
    mocker.patch("shutil.move", side_effect=Exception())
    status_client_mock = mocker.patch("ahriman.core.status.client.Client.set_failed")

    executor.process_build([package_ahriman])
    status_client_mock.assert_called_once()


def test_process_remove_base(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must run remove process for whole base
    """
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[package_ahriman])
    repo_remove_mock = mocker.patch("ahriman.core.alpm.repo.Repo.remove")
    status_client_mock = mocker.patch("ahriman.core.status.client.Client.remove")

    executor.process_remove([package_ahriman.base])
    # must remove via alpm wrapper
    repo_remove_mock.assert_called_once()
    # must update status
    status_client_mock.assert_called_once()


def test_process_remove_base_multiple(executor: Executor, package_python_schedule: Package,
                                      mocker: MockerFixture) -> None:
    """
    must run remove process for whole base with multiple packages
    """
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[package_python_schedule])
    repo_remove_mock = mocker.patch("ahriman.core.alpm.repo.Repo.remove")
    status_client_mock = mocker.patch("ahriman.core.status.client.Client.remove")

    executor.process_remove([package_python_schedule.base])
    # must remove via alpm wrapper
    repo_remove_mock.assert_has_calls([
        mock.call(package, props.filepath)
        for package, props in package_python_schedule.packages.items()
    ], any_order=True)
    # must update status
    status_client_mock.assert_called_once()


def test_process_remove_base_single(executor: Executor, package_python_schedule: Package,
                                    mocker: MockerFixture) -> None:
    """
    must run remove process for single package in base
    """
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[package_python_schedule])
    repo_remove_mock = mocker.patch("ahriman.core.alpm.repo.Repo.remove")
    status_client_mock = mocker.patch("ahriman.core.status.client.Client.remove")

    executor.process_remove(["python2-schedule"])
    # must remove via alpm wrapper
    repo_remove_mock.assert_called_once()
    # must not update status
    status_client_mock.assert_not_called()


def test_process_remove_failed(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
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


def test_process_report(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must process report
    """
    mocker.patch("ahriman.core.repository.executor.Executor.packages", return_value=[package_ahriman])
    mocker.patch("ahriman.core.report.report.Report.load", return_value=Report("x86_64", executor.configuration))
    report_mock = mocker.patch("ahriman.core.report.report.Report.run")

    executor.process_report(["dummy"], [])
    report_mock.assert_called_once()


def test_process_report_auto(executor: Executor, mocker: MockerFixture) -> None:
    """
    must process report in auto mode if no targets supplied
    """
    configuration_getlist_mock = mocker.patch("ahriman.core.configuration.Configuration.getlist")

    executor.process_report(None, [])
    configuration_getlist_mock.assert_called_once()


def test_process_upload(executor: Executor, mocker: MockerFixture) -> None:
    """
    must process sync in auto mode if no targets supplied
    """
    mocker.patch("ahriman.core.upload.upload.Upload.load", return_value=Upload("x86_64", executor.configuration))
    upload_mock = mocker.patch("ahriman.core.upload.upload.Upload.run")

    executor.process_sync(["dummy"], [])
    upload_mock.assert_called_once()


def test_process_upload_auto(executor: Executor, mocker: MockerFixture) -> None:
    """
    must process sync in auto mode if no targets supplied
    """
    configuration_getlist_mock = mocker.patch("ahriman.core.configuration.Configuration.getlist")

    executor.process_sync(None, [])
    configuration_getlist_mock.assert_called_once()


def test_process_update(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must run update process
    """
    mocker.patch("ahriman.models.package.Package.load", return_value=package_ahriman)
    move_mock = mocker.patch("shutil.move")
    repo_add_mock = mocker.patch("ahriman.core.alpm.repo.Repo.add")
    sign_package_mock = mocker.patch("ahriman.core.sign.gpg.GPG.sign_package", side_effect=lambda fn, _: [fn])
    status_client_mock = mocker.patch("ahriman.core.status.client.Client.set_success")

    # must return complete
    assert executor.process_update([package.filepath for package in package_ahriman.packages.values()])
    # must move files (once)
    move_mock.assert_called_once()
    # must sign package
    sign_package_mock.assert_called_once()
    # must add package
    repo_add_mock.assert_called_once()
    # must update status
    status_client_mock.assert_called_once()
    # must clear directory
    from ahriman.core.repository.cleaner import Cleaner
    Cleaner.clear_packages.assert_called_once()


def test_process_update_group(executor: Executor, package_python_schedule: Package,
                              mocker: MockerFixture) -> None:
    """
    must group single packages under one base
    """
    mocker.patch("shutil.move")
    mocker.patch("ahriman.models.package.Package.load", return_value=package_python_schedule)
    repo_add_mock = mocker.patch("ahriman.core.alpm.repo.Repo.add")
    status_client_mock = mocker.patch("ahriman.core.status.client.Client.set_success")

    executor.process_update([package.filepath for package in package_python_schedule.packages.values()])
    repo_add_mock.assert_has_calls([
        mock.call(executor.paths.repository / package.filepath)
        for package in package_python_schedule.packages.values()
    ], any_order=True)
    status_client_mock.assert_called_with(package_python_schedule)


def test_process_empty_filename(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must skip update for package which does not have path
    """
    package_ahriman.packages[package_ahriman.base].filename = None
    mocker.patch("ahriman.models.package.Package.load", return_value=package_ahriman)
    executor.process_update([package.filepath for package in package_ahriman.packages.values()])


def test_process_update_failed(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must process update for failed package
    """
    mocker.patch("shutil.move", side_effect=Exception())
    mocker.patch("ahriman.models.package.Package.load", return_value=package_ahriman)
    status_client_mock = mocker.patch("ahriman.core.status.client.Client.set_failed")

    executor.process_update([package.filepath for package in package_ahriman.packages.values()])
    status_client_mock.assert_called_once()


def test_process_update_failed_on_load(executor: Executor, package_ahriman: Package, mocker: MockerFixture) -> None:
    """
    must process update even with failed package load
    """
    mocker.patch("shutil.move")
    mocker.patch("ahriman.models.package.Package.load", side_effect=Exception())

    assert executor.process_update([package.filepath for package in package_ahriman.packages.values()])
